import getpass
import sys
import os

# For checking callables against the API, & easy mocking
from fabric import api, state
from fabric.main import _escape_split, parse_options, find_fabfile, update_output_levels, load_fabfile, show_commands, display_command, parse_arguments, parse_remainder

from fabric.network import disconnect_all, ssh
from fabric.state import env_options
from fabric.tasks import execute
from fabric.task_utils import crawl
from fabric.utils import abort, indent, warn

import satellite.commands
from satellite.utils import settings, load_settings


def run():
    try:
        # Parse command line options
        parser, options, arguments = parse_options()

        # Handle regular args vs -- args
        arguments = parser.largs
        remainder_arguments = parser.rargs

        if len(arguments) > 1:
            abort("You can call only one command!")

        if arguments:
            tmp_parts = arguments[0].split(':')
            parts = tmp_parts[0].split('.')
            fabfile_locations = ['%s.py' % os.path.join(satellite.commands.__path__[0], *parts[:-1])]
            arguments[0] = parts[-1] + ''.join(":%s" % i for i in tmp_parts[1:])

        # Allow setting of arbitrary env keys.
        # This comes *before* the "specific" env_options so that those may
        # override these ones. Specific should override generic, if somebody
        # was silly enough to specify the same key in both places.
        # E.g. "fab --set shell=foo --shell=bar" should have env.shell set to
        # 'bar', not 'foo'.
        for pair in _escape_split(',', options.env_settings):
            pair = _escape_split('=', pair)
            # "--set x" => set env.x to True
            # "--set x=" => set env.x to ""
            key = pair[0]
            value = True
            if len(pair) == 2:
                value = pair[1]
            state.env[key] = value

        # Update env with any overridden option values
        # NOTE: This needs to remain the first thing that occurs
        # post-parsing, since so many things hinge on the values in env.
        for option in env_options:
            state.env[option.dest] = getattr(options, option.dest)

        # Handle --hosts, --roles, --exclude-hosts (comma separated string =>
        # list)
        for key in ['hosts', 'roles', 'exclude_hosts']:
            if key in state.env and isinstance(state.env[key], basestring):
                state.env[key] = state.env[key].split(',')

        # Handle output control level show/hide
        update_output_levels(show=options.show, hide=options.hide)

        # Handle version number option
        if options.show_version:
            print("Fabric %s" % state.env.version)
            print("Paramiko %s" % ssh.__version__)
            sys.exit(0)

        # Load settings from user settings file, into shared env dict.
        settings.update(load_settings())
        state.env.update(settings.fabric)

        # Find local fabfile path or abort
        fabfile = find_fabfile(fabfile_locations)
        if not fabfile and not remainder_arguments:
            abort("""Couldn't find any fabfiles!

Remember that -f can be used to specify fabfile path, and use -h for help.""")

        # Store absolute path to fabfile in case anyone needs it
        state.env.real_fabfile = fabfile

        # Load fabfile (which calls its module-level code, including
        # tweaks to env values) and put its commands in the shared commands
        # dict
        default = None
        if fabfile:
            docstring, callables, default = load_fabfile(fabfile)
            state.commands.update(callables)

        # Handle case where we were called bare, i.e. just "fab", and print
        # a help message.
        actions = (options.list_commands, options.shortlist, options.display,
                   arguments, remainder_arguments, default)
        if not any(actions):
            parser.print_help()
            sys.exit(1)

        # Abort if no commands found
        if not state.commands and not remainder_arguments:
            abort("Fabfile didn't contain any commands!")

        # Now that we're settled on a fabfile, inform user.
        if state.output.debug:
            if fabfile:
                print("Using fabfile '%s'" % fabfile)
            else:
                print("No fabfile loaded -- remainder command only")

        # Shortlist is now just an alias for the "short" list format;
        # it overrides use of --list-format if somebody were to specify both
        if options.shortlist:
            options.list_format = 'short'
            options.list_commands = True

        # List available commands
        if options.list_commands:
            show_commands(docstring, options.list_format)

        # Handle show (command-specific help) option
        if options.display:
            display_command(options.display)

        # If user didn't specify any commands to run, show help
        if not (arguments or remainder_arguments or default):
            parser.print_help()
            sys.exit(0)  # Or should it exit with error (1)?

        # Parse arguments into commands to run (plus args/kwargs/hosts)
        commands_to_run = parse_arguments(arguments)

        # Parse remainders into a faux "command" to execute
        remainder_command = parse_remainder(remainder_arguments)

        # Figure out if any specified task names are invalid
        unknown_commands = []
        for tup in commands_to_run:
            if crawl(tup[0], state.commands) is None:
                unknown_commands.append(tup[0])

        # Abort if any unknown commands were specified
        if unknown_commands:
            warn("Command(s) not found:\n%s"\
                 % indent(unknown_commands))
            show_commands(None, options.list_format, 1)

        # Generate remainder command and insert into commands, commands_to_run
        if remainder_command:
            r = '<remainder>'
            state.commands[r] = lambda: api.run(remainder_command)
            commands_to_run.append((r, [], {}, [], [], []))

        # Ditto for a default, if found
        if not commands_to_run and default:
            commands_to_run.append((default.name, [], {}, [], [], []))

        # Initial password prompt, if requested
        if options.initial_password_prompt:
            prompt = "Initial value for env.password: "
            state.env.password = getpass.getpass(prompt)

        if state.output.debug:
            names = ", ".join(x[0] for x in commands_to_run)
            print("Commands to run: %s" % names)

        # At this point all commands must exist, so execute them in order.
        for name, args, kwargs, arg_hosts, arg_roles, arg_exclude_hosts in commands_to_run:
            execute(
                name,
                hosts=arg_hosts,
                roles=arg_roles,
                exclude_hosts=arg_exclude_hosts,
                *args, **kwargs
            )
            # If we got here, no errors occurred, so print a final note.
        if state.output.status:
            print("\nDone.")
    except SystemExit:
        # a number of internal functions might raise this one.
        raise
    except KeyboardInterrupt:
        if state.output.status:
            sys.stderr.write("\nStopped.\n")
        sys.exit(1)
    except:
        sys.excepthook(*sys.exc_info())
        # we might leave stale threads if we don't explicitly exit()
        sys.exit(1)
    finally:
        disconnect_all()
    sys.exit(0)
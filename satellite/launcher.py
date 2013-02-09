from optparse import OptionParser
import sys
import os

# For checking callables against the API, & easy mocking
from fabric import state
from fabric.main import find_fabfile, load_fabfile, parse_arguments

from fabric.network import disconnect_all
from fabric.state import env_options
from fabric.tasks import execute
from fabric.utils import abort

import satellite.commands
from satellite.utils import settings, load_settings, get_dir_list, get_task_list, command_exists


def parse_options():
    """
    Handle command-line options with optparse.OptionParser.

    Return list of arguments, largely for use in `parse_arguments`.
    """
    #
    # Initialize
    #

    parser = OptionParser(
        usage=("satellite [options] [<command>"
               "[:arg1,arg2=val2,host=foo,hosts='h1;h2',...]]"))

    parser.add_option('-c', '--config',
        dest='configfile',
        default='satellite.ini',
        metavar='PATH',
        help="specify location of config file to use"
    )

    #
    # Finalize
    #

    # Return three-tuple of parser + the output from parse_args (opt obj, args)
    opts, args = parser.parse_args()
    return parser, opts, args


def print_tree_commands(lvl=1, parts=None):
    parts = parts or []
    path = os.path.join(satellite.commands.__path__[0], *parts)
    prefix = ' '*lvl*2
    if os.path.isdir(path):
        for i in sorted(get_dir_list(path)):
            print prefix + i
            print_tree_commands(lvl+1, parts + [i])
    else:
        for i in sorted(get_task_list(parts)):
            print prefix + i
        print


def run():
    try:
        # Parse command line options
        parser, options, arguments = parse_options()

        # Handle regular args vs -- args
        arguments = parser.largs

        if len(arguments) > 1:
            abort("You can call only one command!")

        if arguments:
            tmp_parts = arguments[0].split(':')
            parts = tmp_parts[0].split('.')
            if not command_exists(parts):
                print
                print 'Warning: command not found!'
                print
                return
            fabfile_locations = ['%s.py' % os.path.join(satellite.commands.__path__[0], *parts[:-1])]
            arguments[0] = parts[-1] + ''.join(":%s" % i for i in tmp_parts[1:])
        else:
            print "Command tree:"
            print_tree_commands()
            return

        # Update env with any overridden option values
        # NOTE: This needs to remain the first thing that occurs
        # post-parsing, since so many things hinge on the values in env.
        for option in env_options:
            state.env[option.dest] = option.default

        # Handle --hosts, --roles, --exclude-hosts (comma separated string =>
        # list)
        for key in ['hosts', 'roles', 'exclude_hosts']:
            if key in state.env and isinstance(state.env[key], basestring):
                state.env[key] = state.env[key].split(',')

        # Load settings from user settings file, into shared env dict.
        settings.update(load_settings(options.configfile))
        state.env.update(settings.fabric)

        # Find local fabfile path or abort
        fabfile = find_fabfile(fabfile_locations)
        if not fabfile:
            abort("""Couldn't find any fabfiles!

Use -h for help.""")

        # Store absolute path to fabfile in case anyone needs it
        state.env.real_fabfile = fabfile

        # Load fabfile (which calls its module-level code, including
        # tweaks to env values) and put its commands in the shared commands
        # dict
        default = None
        if fabfile:
            docstring, callables, default = load_fabfile(fabfile)
            state.commands.update(callables)

        # Abort if no commands found
        if not state.commands:
            abort("Fabfile didn't contain any commands!")

        # Now that we're settled on a fabfile, inform user.
        if state.output.debug:
            if fabfile:
                print("Using fabfile '%s'" % fabfile)
            else:
                print("No fabfile loaded -- remainder command only")


        # Parse arguments into commands to run (plus args/kwargs/hosts)
        commands_to_run = parse_arguments(arguments)

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
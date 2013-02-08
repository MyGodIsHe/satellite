import os

def main():
    """
    Main command-line execution loop.
    """
    if os.environ.has_key('OPTPARSE_AUTO_COMPLETE'):
        from satellite.auto_complete import run
    else:
        from satellite.launcher import run
    run()

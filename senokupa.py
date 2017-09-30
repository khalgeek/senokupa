#!/bin/env python
"""
Monitors the screen saver and runs a command when the screensaver activates
and kills that command when the screensaver deactivates.  The screensaver
must support DBus.
"""

import sys
import argparse
import pydbus
import logging
import subprocess
import shlex
import psutil
import os
import configparser
from gi.repository import GLib

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

config_file = os.path.expanduser('~/.config/senokuparc')

command = None
process = None


def terminate():
    if process is not None:
        logger.debug('Stopping process {0}'.format(process.pid))
        psutil.Process(process.pid).terminate()


def handler(screensaver_active):
    global command
    global process
    logger.debug('Handler reached! Active={0}'.format(screensaver_active))

    if screensaver_active:
        process = subprocess.Popen(command, shell=True)
        logger.debug('Started process {0}'.format(process.pid))
    else:
        if process is not None:
            terminate()


def setup_logging(daemonize):
    formatter = logging.Formatter('%(asctime)s [%(threadName)-12.12s] [%(levelname)-8.8s]  %(message)s')

    if daemonize:
        pass
    else:
        consoleHandler = logging.StreamHandler(sys.stdout)
        consoleHandler.setFormatter(formatter)
        consoleHandler.setLevel(logging.DEBUG)

        logger.addHandler(consoleHandler)
    

def main():
    global command

    parser = argparse.ArgumentParser(description='Runs commands when the screensaver activates')
    parser.add_argument('--daemonize', '-d', action='store_true')
    args = parser.parse_args()

    setup_logging(args.daemonize)
    logger.info('Parsing config at {0}'.format(config_file))

    config = configparser.SafeConfigParser()
    #with open(config_file, 'r') as configfile:
    config.read(config_file)

    logger.debug('{0}'.format(config.sections()))
    command = config.get('Main', 'command')

    logger.debug('Setup DBus')
    bus = pydbus.SessionBus()
    adapter = bus.get('org.freedesktop.ScreenSaver', '/org/freedesktop/ScreenSaver')
    #logger.debug('Active = {0}'.format(adapter.GetActive()))
    adapter.ActiveChanged.connect(handler)


    loop = GLib.MainLoop()

    try:
        logger.debug('Starting main loop')
        loop.run()
    except KeyboardInterrupt:
        terminate()
        loop.quit()

    sys.exit(0)


if __name__ == '__main__':
    main()

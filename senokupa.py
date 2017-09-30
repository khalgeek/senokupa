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
import logging.handlers
import subprocess
import psutil
import os
import configparser
import daemonize
from gi.repository import GLib

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

PID_FILE = '/tmp/senokupa.pid'
CONFIG_FILE = os.path.expanduser('~/.config/senokuparc')

command = None
process = None


def terminate():
    if process is not None:
        logger.info('Stopping process {0}'.format(process.pid))
        psutil.Process(process.pid).terminate()


def handler(screensaver_active):
    global command
    global process
    logger.info('Handler reached! Active={0}'.format(screensaver_active))

    if screensaver_active:
        process = subprocess.Popen(command, shell=True)
        logger.debug('Started process {0}'.format(process.pid))
    else:
        if process is not None:
            terminate()


def setup_logging(daemonize):
    formatter = logging.Formatter('%(asctime)s [%(threadName)-12.12s] [%(levelname)-8.8s]  %(message)s')

    handler = None
    if daemonize:
        handler = logging.handlers.SysLogHandler()
    else:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)

    logger.addHandler(handler)
    

def run_loop():
    logger.debug('Setup DBus')
    bus = pydbus.SessionBus()
    adapter = bus.get('org.freedesktop.ScreenSaver', '/org/freedesktop/ScreenSaver')
    adapter.ActiveChanged.connect(handler)
    
    loop = GLib.MainLoop()

    try:
        logger.debug('Starting main loop')
        loop.run()
    except KeyboardInterrupt:
        terminate()
        loop.quit()


def main():
    global command

    parser = argparse.ArgumentParser(description='Runs commands when the screensaver activates')
    parser.add_argument('--daemonize', '-d', action='store_true', default=False)
    args = parser.parse_args()

    setup_logging(args.daemonize)
    logger.info('Parsing config at {0}'.format(CONFIG_FILE))

    config = configparser.SafeConfigParser()
    config.read(CONFIG_FILE)

    logger.debug('{0}'.format(config.sections()))
    command = config.get('Main', 'command')

    dem = daemonize.Daemonize(app='senokupa', pid=PID_FILE, action=run_loop,
                              foreground=not args.daemonize, logger=logger)
    dem.start()

    sys.exit(0)


if __name__ == '__main__':
    main()

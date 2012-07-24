#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from configparser import ConfigParser
from collections import OrderedDict
import argparse, os.path, itertools, subprocess, re, sys

DEBUG = 'Debug'
RELEASE = 'Release'

def parse_args():
    abspath = os.path.abspath
    global_options = argparse.ArgumentParser(add_help=False)
    add_argument = global_options.add_argument
    add_argument('-v', '--verbose', help='print extra information',
            action='store_true')
    add_argument('-n', '--dry-run', action='store_true',
            help='Print the commands that would be executed, '
            'but do not execute them.')

    parser = argparse.ArgumentParser(description='dcm command line tools.'
            'Note: --dry-run switch implies --verbose')
    parser.set_defaults(configuration=DEBUG, dry_run=False)
    add_argument = parser.add_argument
    add_argument('--version', action='version', version='%(prog)s 0.1')
    subparsers = parser.add_subparsers(help='<cmd> -h for help',
      title='sub commands', dest='action')

    action = subparsers.add_parser('build', help='pack wpf plugin file',
            parents=[global_options])
    add_argument = action.add_argument
    add_argument('-r', '--release', action='store_const', const=RELEASE,
      default=DEBUG, dest='configuration')
    add_argument('projects', nargs='*')

    action = subparsers.add_parser('add', help='Add a project to dcm',
            parents=[global_options])
    add_argument = action.add_argument
    add_argument('name')
    add_argument('path', help='Path to your project', type=abspath)

    return parser.parse_args()

args = parse_args()
del parse_args

class ActionError(Exception):
    pass

def check_action(action):
    ''' run action (command) and check whether it ran successfully

        action() returns None or an int, None or 0 means success, otherwise
        failed. Most of time, action is run directly by main(), but some
        complex action is made by calling many smaller action. When sub action
        is failed, we better abort the executing to prevent more damage.

        check_action() raise ActionError when action() failed, main() catch it
        and set action() result as process exit code.
    '''
    result = action()
    check_action_result(result)

def check_action_result(result):
    if result is not None and result != 0:
        raise ActionError(result)

def quote_if_has_space(strs):
    return ('"{}"'.format(x) if re.search(r'\s', x) else x for x in strs)

def execute(*commandline, **kargs):
    ''' Execute process using commandline, return process exit code
    
        detect args whether args has dry_run argument
    '''
    print(*itertools.chain(quote_if_has_space(commandline), kargs.items()))
    # it seems in cygwin bash environment, python will not flush itself at
    # the end of the line, when executing other process, output is confusing
    sys.stdout.flush()
    if not args.dry_run:
        return subprocess.call(commandline, **kargs)
    else:
        return 0

def build():
    def build_project(p):
        path = config.projects[p]
        cmd_args = [os.path.join(path, 'setup.py'), 'install', '--install-lib']
        cmd_args.append('build/debug' if args.configuration == DEBUG else
                'build/release')
        if args.configuration != DEBUG:
            cmd_args.append('-O2')
        cmd_args.extend(['install_data', '--install-dir'])
        cmd_args.append('build/debug' if args.configuration == DEBUG else
                'build/release')
        cmd_args.extend(['gen_home_pages', '--lib-dir', '~/lib/sf'])
        return execute(*cmd_args, cwd=path)

    for p in args.projects:
        check_action_result(build_project(p))

SECTION_PROJECTS = 'projects'
class Config(object):
    def __init__(self):
        self.projects = OrderedDict()
        self._restore_config()

    @property
    def config_filepath(self):
        return os.path.expanduser('~/.dcm')

    def write(self):
        parser = ConfigParser()
        parser.read(self.config_filepath, 'utf-8')
        def ensure_section(section):
            if not parser.has_section(section):
                parser.add_section(section)

        ensure_section(SECTION_PROJECTS)
        for k, v in self.projects.items():
            parser.set(SECTION_PROJECTS, k, v)

        with open(self.config_filepath, 'w') as f:
            parser.write(f)

    def _restore_config(self):
        parser = ConfigParser()
        parser.read(self.config_filepath, 'utf-8')

        for group, options in parser.items():
            if group == SECTION_PROJECTS:
                self.projects.update(options)

config = Config()

def add():
    config.projects[args.name] = args.path
    config.write()

def main():
    if args.dry_run:
        args.version = True

    try:
        check_action(globals()[args.action])
    except ActionError as e:
        exit(e.args[0])

if __name__ == '__main__':
    main()

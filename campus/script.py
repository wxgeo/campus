# -*- coding: utf-8 -*-
"""
Campus

Created on Wed Oct 13 17:14:48 2021

@author: Nicolas Pourcelot
"""

from argparse import ArgumentParser
from subprocess import run as _run
from os.path import isdir, isfile
from shutil import rmtree, copytree
from pathlib import Path

from .paths import OUTPUT_PATH, STYLE_PATH, PACKAGE_PATH
from .generate_website import generate_website

def run(*args, dry_run=False, **kw):
    'subprocess.run() called with `check=True`.'
    if dry_run:
        print('Execute `%s`' % args)
        return None
    return _run(*args, check=True, **kw)

def main(args=None):
    "Main entry point, called whenever `campus` command is executed."
    parser = ArgumentParser(description='Light content distribution system.')
    subparsers = parser.add_subparsers(help='sub-command help')
    # create the parser for the "init" command
    parser_init = subparsers.add_parser('init', help='a help')
    parser_init.add_argument('--force', action='store_true', help='init --force help')
    parser_init.set_defaults(func=init)

    # create the parser for the "make" command
    parser_make = subparsers.add_parser('make', help='make help')
    parser_make.set_defaults(func=make)

    # create the parser for the "push" command
    parser_push = subparsers.add_parser('push', help='push help')
    parser_push.add_argument('-m', '--message', type=str, help='push -m help')
    parser_push.set_defaults(func=push)

    parsed_args = parser.parse_args(args)

    parsed_args.func(**vars(parsed_args))
    #XXX: campus sans argument devrait renvoyer l'aide !


def init(force=False, **kw):
    "Implement `campus init` command."
    # Copy styles data (ccs and pictures) in a .config folder.
    if force:
        rmtree('.config', ignore_errors=True)
        rmtree(OUTPUT_PATH, ignore_errors=True)
    if isdir('.config'):
        print('Nothing done, since repository seems already configured.\n'
              'Use `campus init --force` if you want to override existing configuration.')
        return
    copytree(STYLE_PATH, '.config')

    # Initialize root folder as a git repository if needed.
    if not isdir('.git'):
        run(['git', 'init'])
    gitignore_OK = False
    if isfile('.gitignore'):
        with open('.gitignore') as f:
            gitignore_OK = any(line.strip() == f'{OUTPUT_PATH.name}/' for line in f)
    if not gitignore_OK:
        with open('.gitignore', 'a') as f:
            f.write(f'\n{OUTPUT_PATH.name}/\n')

    # Create an empty index.md file
    (Path.cwd() / 'index.md').touch()

    # Create the output folder, where the website will be generated.
    if not OUTPUT_PATH.is_dir():
        OUTPUT_PATH.mkdir()
    else:
        print(f"Warning: {OUTPUT_PATH} folder already exist !")

    # Initialize the output folder as a git repository (if needed).
    if not isdir(OUTPUT_PATH / '.git'):
        run(['git', 'init'], cwd=OUTPUT_PATH)


def make(**kw):
    "Implement `campus make` command."
    (OUTPUT_PATH / '.git').replace('.config/tmp_output_git')
    rmtree(OUTPUT_PATH)
    OUTPUT_PATH.mkdir()
    Path('.config/tmp_output_git').replace(OUTPUT_PATH / '.git')
    copytree(Path('.config/css'), OUTPUT_PATH / 'css')
    copytree(Path('.config/pic'), OUTPUT_PATH / 'pic')
    generate_website(Path.cwd(), src=Path.cwd(), dst=OUTPUT_PATH, siblings={})
    print("campus make executed.")


def push(message=None, **kw):
    "Implement `campus push` command."
    # Commit changes in root directory (source), then push.
    commit_cmd = ['git', 'commit', '-a']
    if message:
        commit_cmd.extend(['-m', message])
    run(commit_cmd)
    run(['git', 'push'])

    # Execute `campus make` command.
    make()

    # Commit changes in output directory (website).
    run(commit_cmd, cwd=OUTPUT_PATH)
    run(['git', 'push'], cwd=OUTPUT_PATH)

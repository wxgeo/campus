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
import re

from .paths import OUTPUT_PATH, STYLE_PATH
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
    parser_init = subparsers.add_parser('init', help='initialize folder')
    parser_init.add_argument('--force', action='store_true', help='init --force help')
    parser_init.set_defaults(func=init)

    # create the parser for the "make" command
    parser_make = subparsers.add_parser('make', help='generate website (locally)')
    parser_make.set_defaults(func=make)

    # create the parser for the "push" command
    parser_push = subparsers.add_parser('push', help='generate and upload website')
    parser_push.add_argument('-m', '--message', type=str, help='push -m help')
    parser_push.set_defaults(func=push)

    #create the parser for the "index" command
    parser_index = subparsers.add_parser('index', help='add file to index.md')
    parser_index.add_argument('filename', metavar='FILENAME', type=str,
                              help='add file FILENAME to index.md')
    parser_index.set_defaults(func=index)

    #create the parser for the "indexall" command
    parser_index = subparsers.add_parser('indexall', help='add every file and dir to index.md')
    parser_index.set_defaults(func=indexall)

    parsed_args = parser.parse_args(args)
    try:
        parsed_args.func(**vars(parsed_args))
    except AttributeError:
        parser.print_help()


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
    gitignore_ok = False
    if isfile('.gitignore'):
        with open('.gitignore') as file:
            gitignore_ok = any(line.strip() == f'{OUTPUT_PATH.name}/' for line in file)
    if not gitignore_ok:
        with open('.gitignore', 'a') as file:
            file.write(f'\n{OUTPUT_PATH.name}/\n')

    index()

    # Create the output folder, where the website will be generated.
    if not OUTPUT_PATH.is_dir():
        OUTPUT_PATH.mkdir()
    else:
        print(f"Warning: {OUTPUT_PATH} folder already exist !")

    # Initialize the output folder as a git repository (if needed).
    if not isdir(OUTPUT_PATH / '.git'):
        run(['git', 'init'], cwd=OUTPUT_PATH)

def _add_to_index(path, index_md):
    "Add `path` to index.md file."

    with open(index_md, 'a') as file:
        name = str(path.stem).replace('_', ' ')
        file.write(f'\n[{name}](<{path}>)\n')
        print(f"{name} indexed.")


def index(glob=None, **kw):
    """Implement `campus index` command.

    Generate `index.md` file if needed and add all files matching `glob` to it."""
    # Create an empty index.md file
    current_dir = Path.cwd()
    index_md = (current_dir / 'index.md')
    if not index_md.is_file():
        with open(index_md, 'w') as file:
            file.write(f"# {current_dir.name.replace('_', ' ')}\n\n")
    if glob is None:
        return
    already_indexed = set()
    with open(index_md) as file:
        for line in file:
            match = re.match(r'\s*\[.+\]\(\<?([^<>]+)\>?\)', line)
            if match:
                already_indexed.add(match.group(1))
    indexed = False
    for path in sorted(current_dir.glob(glob)):
        path = Path(path).relative_to(Path.cwd())
        str_path = str(path)
        if (str_path != 'index.md' and str_path[0] != '.'
                                   and str_path not in already_indexed):
            _add_to_index(path, index_md)
            indexed = True
    if not indexed:
        print("It seems there's nothing new to index.")

def indexall(**kw):
    "Implement `campus indexall` command."
    index(glob='*')

def make(**kw):
    "Implement `campus make` command."
    if not Path('.config').is_dir():
        print("WARNING: this folder is not initialized as campus root directory.\n"
              "Change to root directory, or initialized it using `campus init`.")
        return
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

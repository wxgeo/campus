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
import sys
from typing import Optional

from .paths import OUTPUT_PATH, STYLE_PATH
from .generate_website import generate_website, MARKDOWN_LINK

def run(*args, dry_run=False, **kw):
    'subprocess.run() called with `check=True`.'
    if dry_run:
        print('Execute `%s`' % args)
        return None
    return _run(*args, check=True, **kw)

def main(args: Optional[list] = None) -> None:
    "Main entry point, called whenever `campus` command is executed."
    parser = ArgumentParser(description='Light content distribution system.')
    subparsers = parser.add_subparsers(help='sub-command help')
    add_parser = subparsers.add_parser
    # create the parser for the "init" command
    parser_init = add_parser('init', help='initialize folder')
    parser_init.add_argument('--force', action='store_true', help='init --force help')
    parser_init.set_defaults(func=init)

    # create the parser for the "make" command
    parser_make = add_parser('make', help='generate website (locally)')
    parser_make.set_defaults(func=make)

    # create the parser for the "push" command
    parser_push = add_parser('push', help='generate and upload website')
    parser_push.add_argument('-m', '--message', type=str, help='push -m help')
    parser_push.set_defaults(func=push)

    #create the parser for the "index" command
    parser_index = add_parser('index', help='add file to index.md')
    parser_index.add_argument('glob', metavar='FILENAME', type=str,
                              help='Add file FILENAME to index.md.\n'
                                   'Wildcars are supported ("chap*.pdf").')
    parser_index.add_argument('-r', '--recursive', action='store_true',
                              help='index --recursive help')
    parser_index.add_argument('-f', '--create', action='store_true',
                              help='Create index.md file if not found.')
    parser_index.set_defaults(func=index)

    #create the parser for the "indexall" command
    parser_indexall = add_parser('indexall',
                                 help='Index every file and directory recursively.')
    parser_indexall.add_argument('-f', '--create', action='store_true',
                                 help='Create index.md file if not found.')
    parser_indexall.set_defaults(func=indexall)

    parsed_args = parser.parse_args(args)
    try:
        # Launch the function corresponding to the given subcommand.
        kwargs = vars(parsed_args)
        kwargs.pop('func')(**kwargs)
    except KeyError:
        # No subcommand passed.
        parser.print_help()


def init(force: bool = False) -> None:
    "Implement `campus init` command."
    # Copy styles data (ccs and pictures) in a .config folder.
    if force:
        rmtree('.campus-config', ignore_errors=True)
        rmtree(OUTPUT_PATH, ignore_errors=True)
    if isdir('.campus-config'):
        print('Nothing done, since repository seems already configured.\n'
              'Use `campus init --force` if you want to override existing configuration.')
        return
    copytree(STYLE_PATH, '.campus-config')

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

    index(create=True)

    # Create the output folder, where the website will be generated.
    if not OUTPUT_PATH.is_dir():
        OUTPUT_PATH.mkdir()
    else:
        print(f"Warning: {OUTPUT_PATH} folder already exist !")

    # Initialize the output folder as a git repository (if needed).
    if not isdir(OUTPUT_PATH / '.git'):
        run(['git', 'init'], cwd=OUTPUT_PATH)


def _test_init() -> None:
    "Decorator function to assert "
    if not Path('.campus-config').is_dir():
        print("WARNING: for security, this command can only be launched in an"
              " initialized campus root directory.\n"
              "Change to root directory, or initialized it using `campus init`.")
        sys.exit(1)


def _add_to_index(path: Path, index_md: Path) -> None:
    "Add `path` to index.md file."

    with open(index_md, 'a', encoding='utf8') as file:
        name = str(path.stem).replace('_', ' ')
        file.write(f'\n[{name}](<{path}>)\n')
        print(f"{name} indexed.")


def _index(glob: str, parent: Path, recursive: bool = False) -> bool:
    """Implement `campus index` command.

    Generate `index.md` file if needed and add all files matching `glob` to it.

    Hidden files or directories, ie. those starting with a dot (".mydir", ".myfile"),
     are never indexed, though you may add them manually to a `index.md` file.
    """
    # Create an empty index.md file
    something_indexed = False
    if recursive:
        # Index all subdirectories content.
        for child in sorted(parent.glob('*')):
            # Skip hidden directories (directories whose name starts with a dot).
            if child.is_dir() and child.name[0] != '.':
                something_indexed |= _index(glob, child, recursive=True)
    index_md = (parent / 'index.md')
    if not index_md.is_file():
        with open(index_md, 'w', encoding='utf8') as file:
            file.write(f"# {parent.name.replace('_', ' ')}\n\n")
        print(f"'{index_md}' file created.")
    if not glob:
        return False
    already_indexed = set()
    with open(index_md, encoding='utf8') as file:
        for line in file:
            match = re.match(MARKDOWN_LINK, line)
            if match:
                already_indexed.add(match.group(1))
    for child in sorted(parent.glob(glob)):
        child = Path(child).relative_to(parent)
        name = child.name
        if (name != 'index.md' and name[0] != '.' and name not in already_indexed):
            _add_to_index(child, index_md)
            something_indexed = True
    return something_indexed


def index(glob: str = '', recursive: bool = False, create: bool = False) -> None:
    """Implement `campus index` command.

    Generate `index.md` file if needed and add all files matching `glob` to it.

    Hidden files or directories, ie. those starting with a dot (".mydir", ".myfile"),
     are never indexed, though you may add them manually to a `index.md` file.
    """
    if not Path('index.md').is_file() and not create:
        print("WARNING: trying to use `campus index` in a directory "
              "which doesn't have an `index.md` file.\n"
              "Use `--create` option if you want to create a new index.md file.")
        sys.exit(1)
    if not glob and not create:
        print("WARNING: campus index argument missing !")
    if not _index(glob, parent=Path.cwd(), recursive=recursive):
        print(f"It seems there's nothing new to index.")


def indexall(create: bool = False) -> None:
    "Implement `campus indexall` command."
    index(glob='*', recursive=True, create=create)


def make() -> None:
    "Implement `campus make` command."
    _test_init()
    (OUTPUT_PATH / '.git').replace('.campus-config/tmp_output_git')
    rmtree(OUTPUT_PATH)
    OUTPUT_PATH.mkdir()
    Path('.campus-config/tmp_output_git').replace(OUTPUT_PATH / '.git')
    copytree(Path('.campus-config/css'), OUTPUT_PATH / 'css')
    copytree(Path('.campus-config/pic'), OUTPUT_PATH / 'pic')
    generate_website(Path.cwd(), src=Path.cwd(), dst=OUTPUT_PATH, siblings={})
    print("campus make executed.")


def push(message: str = '') -> None:
    "Implement `campus push` command."
    _test_init()
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

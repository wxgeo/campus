# -*- coding: utf-8 -*-
"""
Campus

Created on Wed Oct 13 17:14:48 2021

@author: Nicolas Pourcelot
"""

from argparse import ArgumentParser
from subprocess import run as _run
from os.path import isdir
from shutil import rmtree, copytree
from pathlib import Path

from paths import OUTPUT_PATH, STYLE_PATH

def run(*args, dry_run=True, **kw):
    kw.setdefault('check', True)
    if dry_run:
        print('Execute `%s`' % ' '.join(args))
    else:
        _run(*args, **kw)

def main(args=None):
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


def init(force=False):
    "Implement `campus init` command."
    # Copy styles data (ccs and pictures) in a .config folder.
    if force:
        rmtree('.config')
    if isdir('.config'):
        print('Nothing done, since repository seems already configured.\n'
              'Use `campus init --force` if you want to override existing configuration.')
        return
    else:
        copytree(STYLE_PATH, '.config')

    # Initialize root folder as a git repository if needed.
    if not isdir('.git'):
        run(['git', 'init'])

    # Create an empty index.md file
    open(Path.cwd() / 'index.md').close()

    # Create the output folder, where the website will be generated.
    if not OUTPUT_PATH.is_dir():
        OUTPUT_PATH.mkdir()
    else:
        print(f"Warning: {OUTPUT_PATH} folder already exist !")

    # Initialize the output folder as a git repository (if needed).
    if not isdir(OUTPUT_PATH / '.git'):
        run(['git', 'init'], cwd=OUTPUT_PATH)


def make():
    "Implement `campus make` command."
    print("campus make")


def push(message=None):
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




















#from os import makedirs
#from os.path import join, realpath, expanduser, isdir
#from shutil import rmtree, copytree
#
#from generate_index import generate_index
#
##<DEBUG>
#import sys
#sys.argv = ['compile.py', '~/Dropbox/Test-TR']
##</DEBUG>
#
#parser = argparse.ArgumentParser()
#parser.add_argument('path', default='.', nargs='?')
#args = parser.parse_args()
#
#
## Création d'un dossier HTML
#ROOT = realpath(expanduser(args.path))
#
#HTML_DIR = join(ROOT, 'html')
#CSS = join(HTML_DIR, 'css')
#PIC = join(HTML_DIR, 'pic')
#
## Test if a css directory exists as a (minimal) precaution.
#if isdir(CSS):
#    rmtree(HTML_DIR)
#makedirs(HTML_DIR)
#copytree(join(ROOT, '.config', 'css'), CSS)
#copytree(join(ROOT, '.config', 'pic'), PIC)
#generate_index(ROOT, src=ROOT, dst=HTML_DIR)





# ------------------------------
# On parcourt le dossier
#for root, dirs, files in walk(path):
#    try:
#        dirs.remove('html')
#    except ValueError:
#        pass
#    if 'index.md' in files:
#        output = join(root, 'index.html')
#        md_file = join(root, 'index.md')
#        generate(output, md_file, TEMPLATE)


#with open(join(path, 'index.md'))



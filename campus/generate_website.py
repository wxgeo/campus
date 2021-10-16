# -*- coding: utf-8 -*-
"""
Campus

Created on Thu Sep 26 10:26:48 2019

@author: Nicolas Pourcelot

Balises spéciales :
    [$MAIN]
    [$NAV]
    [$NEXT]
    [$PREVIOUS]


Algorithme :
On part de la racine du dossier local.
On lit tous les fichiers index.md -> index.html
Tous les fichiers indexés sont copiés dans le dossier html,
en respectant l'arborescence.

Difficulté :
tous les fichiers index.html doivent avoir une barre de navigation
automatiquement incorporée.
pour cela, il suffit de chercher les dossiers frères, et de garder uniquement
ceux qui sont indexés.

On peut commencer par générer un dictionnaire :
{path_to_an_index_md_file: [(href_in_the_file, title)]}


"""
from re import findall, search
from shutil import copy

from mistune import markdown

from .paths import INDEX_TEMPLATE_PATH, Path


def assert_relative_to(path, src):
    "Raise a `ValueError` if path is not relative to `src`."
    try:
        path.relative_to(src)
    except ValueError:
        raise ValueError(f'"{path}" should be a subdirectory of "{src}".')


def translate_path(path: Path, src, dst: Path) -> Path:
    "Transform {src}/subpath into {dst}/subpath."
    assert_relative_to(path, src)
    return dst / path.relative_to(src)


def relative_depth(path: Path, src: Path) -> int:
    "Return the depth of the given path relatively to src."
    assert_relative_to(path, src)
    return len(path.parents) - len(src.parents)


#def _link_to(current: str, links: dict, step: int) -> str:
#    "Generate an <a> tag for `current` link, using `links` dictionnary."
#    hrefs = list(links)
#    try:
#        i = (hrefs.index(current) + 1) % len(hrefs)
#    except ValueError:
#        return ''
#    href = hrefs[i]
#    title = links[href]
#    return f'<a href="../{href}">{title}</a>'
#
#
#def link_to_next(current: str, links: dict) -> str:
#    return _link_to(current, links, 1)
#
#
#def link_to_previous(current: str, links: dict) -> str:
#    return _link_to(current, links, -1)


def find_links(path: Path, html: str) -> dict:
    """Extract all links from html code.

    Return a dict with the following format:
    {'directories': {'name': 'path'}, 'files': {'name': 'path'}}
    """
    #print(path)
    all_links = findall(r'<a href="([^"]+)">([^<]+)</a>', html)
    directories = {}
    files = {}
    #print(all_links)
    for link, title in all_links:
        _link = path / link
        # List links that point to directories.
        if _link.is_dir():
            directories[link] = title
            # links must be left relative, so we won't need to convert them
            # when generating the navigation bar.
        elif _link.is_file():
            files[link] = title
        else:
            print(f"WARNING: {_link!r} is referenced but not found.")

    return {'directories': directories, 'files': files}


def find_title(html: str) -> str:
    "Return <h1> title content."
    m = search('<h1>([^<]+)</h1>', html)
    return m.group(1) if m else None


def generate_nav(links: dict, parent=True) -> str:
    """Generate the navigation menu content.

    `links` dict format is {'href': 'title'}"""
    content = ['<ol>']
    if parent:
        content.append('<li><a href="..">..&nbsp;&nbsp;</a></li>')
    for href, title in links.items():
        content.append('<li>')
        content.append(f'<a href="../{href}">')
        content.append(title)
        content.append('</a>')
        content.append('</li>')
    content.append('</ol>')
    return '\n'.join(content)


def generate_website(directory: Path, src: Path, dst: Path, siblings: dict, title=''):
    """Recursively generate website :
        - generate `index.html` files from the `index.md` files.
        - copy index.html files and all tracked files to output directory.
    """
    # Convert Markdown to HTML
    index_file = directory / 'index.md'
    if not index_file.is_file():
        print(f"WARNING: {directory!r} has no 'index.md' file.")
        main = ''
    else:
        with open(index_file, encoding='utf8') as f:
            main = markdown(f.read(), escape=False)

    # Extract page title (it will be reinjected later).
    main_title = find_title(main)
    if main_title is not None:
        title = main_title
        # Avoid the <h1> title to appear twice !
        # (It will be automatically generated in <header>.)
        main = main.replace(f'<h1>{title}</h1>', '')

    # Add stylesheet
    depth = relative_depth(directory, src=src)
    css_relative_path = Path(*(depth*['..'])) / 'css'
    css_name = f'{depth}.css'
    if not (dst / 'css' / css_name).is_file():
        css_name = 'default.css'

    # current = directory.name
    data = {'common_stylesheet': css_relative_path / 'all.css',
            'stylesheet': css_relative_path / css_name,
            'nav': generate_nav(siblings, parent=(directory != src)),
            'main': main,
            # 'previous': link_to_previous(current, siblings),
            # 'next': link_to_next(current, siblings),
            'title': title,
            }
    with open(INDEX_TEMPLATE_PATH, encoding='utf8') as f:
        html = f.read()
    for key in data:
        html = html.replace(f'[${key.upper()}]', str(data[key]))

    links = find_links(directory, main)

    output_dir = translate_path(directory, src, dst)
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / 'index.html', 'w', encoding='utf8') as f:
        f.write(html)

    for link, title in links['files'].items():
        src_file = directory / link
        dst_file = translate_path(src_file, src, dst)
        copy(src_file, dst_file)

    for link, title in links['directories'].items():
        path = directory / link
        generate_website(path, src, dst, siblings=links['directories'], title=title)


#def generate_modules():
#    pass
#
#
#def generate_chapters():
#    pass

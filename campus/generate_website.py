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
from re import sub, search, Match
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


def extract_links(path: Path, html: str) -> ({str: {str: str}}, str):
    """Extract all links from html code, and add a <span> tag before them.

    The class of the <span> tag will specify the type of link, and may be used
    by the stylesheet later.

    Return a tuple with the following format:
    ({'directories': {'name': 'path'}, 'files': {'name': 'path'}}, 'HTML code')
    """
    directories = {}
    files = {}

    def classify(match: Match):
        "Classify links (is it directory or a file ?)."
        # This is an internet link, pass...
        string = match.group(0)
        if '://' in string:
            return string
        link, title = match.groups()
        _link = path / link
        # Store links that point to directories.
        if _link.is_dir():
            directories[link] = title
            css_class = '"before directory"'
        # Store links that point to files.
        elif _link.is_file():
            files[link] = title
            css_class = f'"before file {_link.suffix[1:]}"'
        # Neither directory nor file: this is a broken link !
        else:
            print(f"WARNING: '{_link!s}' link seems to be broken !")
            css_class = '"before broken-link"'
        return f"<span class={css_class}></span>{string}"

    html = sub(r'<a href="([^"]+)">([^<]+)</a>', classify, html)

    return {'directories': directories, 'files': files}, html


def find_title(html: str) -> str:
    "Return <h1> title content."
    match = search('<h1>([^<]+)</h1>', html)
    return match.group(1) if match else None


def generate_nav(links: dict, directory: Path, parent=True) -> str:
    """Generate the navigation menu content.

    `links` dict format is {'href': 'title'}"""
    content = ['<ol>']
    if parent:
        content.append('<li><a href="..">..</a></li>')
    for link, title in links.items():
        href = f'../{link}'
        # The `current` css class is used to indicate that the link is actually
        # pointing to the current page.
        css_class = 'current' if (directory / href).resolve() == directory else ''
        content.append(f'<li><a href="{href}" class="{css_class}">{title}</a></li>')
    content.append('</ol>')
    return '\n'.join(content)


def read_index_md_as_html(directory: Path) -> str:
    "Read index.md file and return corresponding HTML."
    # Convert Markdown to HTML
    index_file = directory / 'index.md'
    if not index_file.is_file():
        print(f'WARNING: "{directory}" has no "index.md" file.')
        main = ''
    else:
        with open(index_file, encoding='utf8') as file:
            main = markdown(file.read(), escape=False)
    return main


def generate_website(directory: Path, src: Path, dst: Path, siblings: dict, title=''):
    """Recursively generate website :
        - generate `index.html` files from the `index.md` files.
        - copy index.html files and all tracked files to output directory.
    """
    assert all(isinstance(d, Path) for d in (directory, src, dst))
    main = read_index_md_as_html(directory)

    # Extract page title (it will be reinjected later).
    main_title = find_title(main)
    if main_title is not None:
        title = main_title
        # Avoid the <h1> title to appear twice !
        # (It will be automatically generated in <header>.)
        main = main.replace(f'<h1>{title}</h1>', '')

    links, main = extract_links(directory, main)

    # Add stylesheet
    depth = relative_depth(directory, src=src)
    css_relative_path = Path(*(depth*['..'])) / 'css'
    css_name = f'{depth}.css'
    if not (dst / 'css' / css_name).is_file():
        css_name = 'default.css'


    data = {'common_stylesheet': css_relative_path / 'all.css',
            'stylesheet': css_relative_path / css_name,
            'nav': generate_nav(siblings, directory, parent=(directory != src)),
            'main': main,
            'title': title,
            }
    with open(INDEX_TEMPLATE_PATH, encoding='utf8') as file:
        html = file.read()
    for key in data:
        html = html.replace(f'[${key.upper()}]', str(data[key]))

    output_dir = translate_path(directory, src, dst)
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / 'index.html', 'w', encoding='utf8') as file:
        file.write(html)

    for link, _ in links['files'].items():
        src_file = directory / link
        dst_file = translate_path(src_file, src, dst)
        copy(src_file, dst_file)

    for link, txt in links['directories'].items():
        path = directory / link
        generate_website(path, src, dst, siblings=links['directories'], title=txt)


#def generate_modules():
#    pass
#
#
#def generate_chapters():
#    pass

import os
import pathlib
from re import sub
import sys

from django.template import Template

import click


def file_from_template(path, dest_path, context=None):
    if path.is_dir():
        dest_path.mkdir(parents=True, exist_ok=True)
        return

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    contents = path.read_text()

    if context is None:
        to_write = contents
    else:
        to_write = Template(contents).render(context)

    dest_path.write_text(to_write)


@click.group()
def cli():
    pass


def camel_case(s):
    # Use regular expression substitution to replace underscores and hyphens with spaces,
    # then title case the string (capitalize the first letter of each word), and remove spaces
    return sub(r"(_|-)+", " ", s).title().replace(" ", "")


def get_app():
    sys.path.insert(0, f'{pathlib.Path.cwd()}')

    from website import app

    return app


@cli.command()
@click.option('--target', default='.', help='Target direcotory in which to start your project')
def init(target):
    '''Initialize your calico app in the specified directory'''
    import calico

    target_path = pathlib.Path(target)
    module_template_path = pathlib.Path(calico.__file__).parent / 'templates' / 'calico'

    for path in (module_template_path / 'content').rglob('*'):
        rel_path = path.relative_to(module_template_path)
        dest_path = target_path / rel_path
        file_from_template(path, dest_path)

    for rel_path in ('website.py', 'public/.gitkeep'):
        path = module_template_path / rel_path
        dest_path = target_path / rel_path
        file_from_template(path, dest_path)


@cli.command()
@click.option('--target', default='dist')
@click.option('--noinput', is_flag=True, default=False)
def build(target, noinput):
    '''
    Build static website in the specified directory
    '''
    os.environ.setdefault('DEBUG', 'False')
    app = get_app()

    collect_args = ['collectstatic']
    distill_args = ['distill-local']

    if noinput:
        collect_args.append('--noinput')
        distill_args.append('--force')

    distill_args.append(target)

    app.manage(collect_args)
    app.manage(distill_args)


@cli.command()
@click.argument('args', type=str, required=False, nargs=-1)
def manage(args):
    '''
    Run a management command
    '''
    app = get_app()
    app.manage(args)


@cli.command()
@click.argument('host', type=str, required=False, default='')
def run(host):
    '''
    Start the app in development mode on the specified IP and port
    '''
    app = get_app()
    app.run(host)


@cli.command()
@click.argument('slug')
@click.argument('to_file', required=False, default='main.md')
def single_to_multi_file(slug, to_file):
    '''
    Move page from a single-file page to a multi-file page.
    '''
    import frontmatter
    import yaml

    get_app()  # required to load settings
    from calico.models import Page

    page = Page(slug)
    assert page._is_single_file, f'{slug} is already multi-file'

    page_dir = page.base_path / slug
    page_dir.mkdir(mode=0o755)

    meta = page.get_files()[0].metadata
    widget = meta.pop('widget', 'text')
    with open(page_dir / 'data.yml', 'w') as fm:
        yaml.dump(meta, fm)

    post = frontmatter.Post(page.md_content)
    post['weight'] = 0
    post['widget'] = widget
    with open(page_dir / to_file, 'wb') as md:
        frontmatter.dump(post, md)

    (page.base_path / f'{slug}.md').unlink()

    print(f'✔️  {page_dir}.md ➡️ {page_dir}/')


@cli.command
@click.argument('name')
def start_plugin(name):
    '''
    Initialize a local plugin.
    A plugin is an auto-loading Django app (startapp) with extra features
    '''
    from django.template import Context
    from django.utils.text import slugify

    import calico

    get_app()  # app needs to be initialized to use the template engine

    target_dir_name = slugify(name).replace('-', '_')
    camel_name = camel_case(target_dir_name)

    target_path = pathlib.Path.cwd() / 'plugins' / target_dir_name

    module_template_path = pathlib.Path(calico.__file__).parent / 'templates' / 'calico_plugin'

    context = Context({
        'name': name,
        'camel_name': camel_name,
        'module_name': target_dir_name,
    })

    for path in module_template_path.rglob('*'):
        rel_path = path.relative_to(module_template_path)
        dest_path = target_path / rel_path
        file_from_template(path, dest_path, context)

    print(f'✔️  Created plugin plugins/{target_dir_name}')


@cli.command
def show_media():
    '''
    Shows the list of loaded media and their associated label if any
    '''
    from pprint import pprint
    from calico import calico_media

    app = get_app()
    for media in ('css', 'js'):
        extra = getattr(app, f'_{media}')
        print(media)
        for label, sources in calico_media(media, app._theme, raw=True, extra=extra).items():
            print(f'- {label}:', end=' ')
            pprint(sources)


if __name__ == '__main__':
    cli()

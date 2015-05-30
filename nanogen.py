"""
nanogen - a very small static site generator
"""
import os
import re
import logging
import datetime
import subprocess

import yaml
import click
import jinja2
import renderer

from logger import log


__version__ = '0.6.0'
__author__ = 'Bill Israel <bill.israel@gmail.com>'

PATHS = {
    'cwd': os.getcwd(),
    'site': os.path.join(os.getcwd(), '_site'),
    'posts': os.path.join(os.getcwd(), '_posts'),
    'layouts': os.path.join(os.getcwd(), '_layouts'),
}

FM_SEPARATOR = '----'

JINJA_LOADER = jinja2.FileSystemLoader([PATHS['cwd'], PATHS['layouts']])
JINJA_ENV = jinja2.Environment(loader=JINJA_LOADER)

class Post(object):
    """Represents a post."""
    def __init__(self, path_to_file):
        log.info('Processing post at %s', path_to_file)
        self.markdown = renderer.markdown
        self.path = path_to_file
        self.filename = self.path.split('/')[-1]

        with open(self.path, 'r') as p:
            p_full = p.read()

        p_split = p_full.split(FM_SEPARATOR)
        if len(p_split) == 3:
            self.config = yaml.safe_load(p_split[1])
            content_raw = p_split[2].strip()
        else:
            self.config = yaml.safe_load(p_split[0])
            content_raw = p_split[1].strip()

        self.content = self.markdown(content_raw)

    def __getattr__(self, item):
        """
        Attempt to find the "missing" attribute in the post's configuration.
        """
        if item in self.config:
            return self.config[item]
        log.warning('Unable to locate attribute %s', item)
        return None

    def __repr__(self):
        return u'<Post {}>'.format(self.filename)

    @property
    def pub_date(self):
        year, month, day = map(int, self.filename.split('-', 3)[:3])
        return datetime.datetime(year=year, month=month, day=day)

    @property
    def slug(self):
        if 'slug' in self.config:
            _slug = self.config['slug']
        else:
            _slug = '-'.join(self.filename.split('-', 3)[3:]).rsplit('.', 1)[0]
        return _slug

    @property
    def html_filename(self):
        return '{}.html'.format(self.slug)

    @property
    def permapath(self):
        dt = self.pub_date
        return os.path.join(PATHS['site'], str(dt.year),
                            '{:02d}'.format(dt.month), self.html_filename)

    @property
    def permalink(self):
        dt = self.pub_date
        return '/{}/{:02d}/{}'.format(dt.year, dt.month, self.html_filename)


def _read_config():
    """Read the config YAML file (if it exists), and return it as a dict.

    :return dict: the configuration dictionary
    """
    log.info('Reading configuration...')
    cfg_file = os.path.join(PATHS['cwd'], 'config.yaml')
    if os.path.isfile(cfg_file):
        with open(cfg_file, 'r') as cf:
            return yaml.safe_load(cf.read())
    else:
        log.warning('Warning: no configuration file found.')

    return {}


def _is_valid_post_file(path):
    """
    Determines if the given path is valid for a post file.

    The criteria:
        1. The file can't start with an underscore; these are ignored
        2. The file's name must match the pattern yyyy-mm-dd-*
        3. The file's extension must be a valid Markdown extension

    :param path: The file path to validate
    """
    post_pattern = r'^\d{4}-\d{2}-\d{2}-.*'
    markdown_extenstions = ['md', 'markdown', 'mdown']

    filename, ext = os.path.basename(path).rsplit('.', 1)

    ignored = not filename.startswith('_')
    valid_filename = re.match(post_pattern, filename)
    valid_ext = ext in markdown_extenstions

    return ignored and valid_filename and valid_ext


def _clean():
    log.info('Cleaning generated files...')
    site_dir = PATHS['site']
    if os.path.isdir(site_dir):
        subprocess.call(['rm', '-r', site_dir])


@click.group()
@click.option('-v', '--verbose', count=True, help='Turn on verbose output.')
@click.pass_context
def cli(ctx, verbose):
    if verbose == 1:
        log.setLevel(logging.INFO)

    if verbose > 1:
        log.setLevel(logging.DEBUG)

@cli.command()
@click.pass_context
def init(ctx):
    """Initialize the current directory."""
    for d in [PATHS['posts'], PATHS['templates']]:
        log.debug('Creating directory %s' % d)
        if not os.path.isdir(d):
            subprocess.call(['mkdir', d])


@cli.command()
@click.pass_context
def clean(ctx):
    """Clean any generated files."""
    _clean()


@cli.command()
@click.pass_context
def build(ctx):
    """Start a build of the site."""
    _clean()
    config = _read_config()

    if not os.path.isdir(PATHS['site']):
        log.debug('Creating site directory...')
        subprocess.call(['mkdir', PATHS['site']])

    log.info('Processing posts...')
    ls = os.listdir(PATHS['posts'])
    post_path = lambda path: os.path.join(PATHS['posts'], path)
    posts = [Post(post_path(p)) for p in ls if _is_valid_post_file(p)]

    for post in posts:
        log.debug('Rendering template for post %s', post.path)
        template = JINJA_ENV.get_template(post.layout or 'article.html')
        html = template.render(site=config, post=post)

        post_dir = os.path.dirname(post.permapath)
        if not os.path.isdir(post_dir):
            log.debug('Creating post directory %s', post_dir)
            subprocess.call(['mkdir', '-p', post_dir])

        log.debug('Writing post to %s', post.permapath)
        with open(post.permapath, 'w') as pout:
            pout.write(html)

    log.info('Processing non-post files...')
    for dirpath, subdirs, files in os.walk(PATHS['cwd']):
        subdirs[:] = [d for d in subdirs if not d.startswith('_')]
        files[:] = [f for f in files if f.endswith('.html') or f.endswith('.xml')]
        rel_path = dirpath.replace(PATHS['cwd'], '').strip('/')

        for f in files:
            log.debug('Processing %s', f)
            template = JINJA_ENV.get_template(f)
            html = template.render(site=config, posts=posts)

            file_dir = os.path.join(PATHS['site'], rel_path)

            if not os.path.isdir(file_dir):
                log.debug('Creating directory %s', file_dir)
                subprocess.call(['mkdir', '-p', os.path.dirname(file_dir)])

            file_path = os.path.join(file_dir, f)
            log.debug('Writing %s to %s', f, file_path)
            with open(file_path, 'w') as pout:
                pout.write(html)

        if rel_path in config.get('keep', []):
            log.debug('Keeping directory %s', rel_path)
            subdirs[:] = []

            file_dir = os.path.join(PATHS['site'], rel_path)

            if not os.path.isdir(file_dir):
                log.debug('Creating directory %s', file_dir)
                subprocess.call(['mkdir', '-p', file_dir])

            copy_path = os.path.join(PATHS['site'], rel_path)
            log.debug('Recursively copying %s to %s', dirpath, copy_path)
            subprocess.call(['cp', '-r', dirpath, PATHS['site']])

    click.secho('Done.', fg='green')

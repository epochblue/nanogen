"""
gin - a very small static site generator

Usage:
    gin init [PATH]
    gin build
    gin clean

Options:
    -h --help       Show this message.
    --version       Show version.
"""
from __future__ import absolute_import, print_function

import os
import subprocess
from datetime import datetime

import yaml
import jinja2
import docopt
import markdown

__all__ = ['main']
__version__ = '0.3.1'
__author__ = 'Bill Israel <bill.israel@gmail.com>'

CONFIG_FILE = 'config.yaml'

FM_SEPARATOR = '----'

TEMPLATES = {
    'POST': 'article.html',
    'PAGE': 'article.html',
    'COLLECTIONS': {
        'INDEX': 'index.html',
        'ARCHIVE': 'archive.html',
        'RSS': 'rss.xml'
    }
}

DIRS = {
    'POSTS': '_posts',
    'PAGES': '_pages',
    'STATIC': '_static',
    'TEMPLATES': '_templates',
    'DRAFTS': '_drafts',
    'SITE': 'site'
}

TEMPLATE_PATH = os.path.join(os.path.abspath(os.getcwd()), DIRS['TEMPLATES'])

JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_PATH))


class Post(object):
    """Represents a post."""
    def __init__(self, path, fname):
        split_fname = fname.split('-')
        d = '{}-{}-{}'.format(split_fname[0], split_fname[1], split_fname[2])

        self.publish_date = datetime.strptime(d, '%Y-%m-%d')
        self.site_path = os.path.join(path, DIRS['SITE'])
        self.file_path = os.path.join(path, DIRS['POSTS'], fname)

        self.publish_folder = '{}/{}'.format(self.publish_date.year,
                                             self.publish_date.month)
        pub_path = '{}/{}-{}'.format(self.publish_folder,
                                     split_fname[2],
                                     split_fname[3])

        self.publish_path = os.path.join(self.site_path, pub_path)

        with open(self.file_path, 'r') as f: 
            file_str = f.read()
        
        split_file = file_str.split(FM_SEPARATOR)
        self.front_matter = yaml.load(split_file[1])
        self.content = markdown.markdown(split_file[2].strip())

        # Process the title differently, in case it has Markdown in it
        title = self.front_matter.pop('title')
        self.title = markdown.markdown(title.strip())
        self.title = self.title.replace('<p>', '').replace('</p>', '')  # ew

        for key, value in self.front_matter.items():
            setattr(self, key, value)

    @property
    def permalink(self):
        return '{}/{}/{}.html'.format(self.publish_date.year,
                                      self.publish_date.month,
                                      self.slug)

    @property
    def filename(self):
        return '{}.html'.format(self.slug)

    @property
    def path(self):
        return os.path.join(self.site_path,
                            str(self.publish_date.year),
                            str(self.publish_date.month),
                            self.filename)

    @property
    def layout(self):
        return self.front_matter.get('template')


class Page(object):
    """Represents a page."""
    def __init__(self, path, fname):
        self.file_path = os.path.join(path, DIRS['PAGES'], fname)
        self.publish_path = os.path.join(path, DIRS['SITE'])

        with open(self.file_path, 'r') as f:
            file_str = f.read()

        split_file = file_str.split(FM_SEPARATOR)
        self.front_matter = yaml.load(split_file[1])
        self.content = markdown.markdown(split_file[2].strip())

        # Process the title differently, in case it has Markdown in it
        title = self.front_matter.pop('title')
        self.title = markdown.markdown(title.strip())
        self.title = self.title.replace('<p>', '').replace('</p>', '')  # ew

        for key, value in self.front_matter.items():
            setattr(self, key, value)

    @property
    def permalink(self):
        return '{}.html'.format(self.slug)

    @property
    def filename(self):
        return '{}.html'.format(self.slug)

    @property
    def path(self):
        return os.path.join(self.site_path,
                            self.filename)

    @property
    def layout(self):
        return self.front_matter.get('template')


def _initialize_blog_dir(path):
    file_path = os.path.join(path, CONFIG_FILE)
    if not os.path.exists(file_path):
        subprocess.call(['touch', file_path])

    for d in DIRS.values():
        dir_path = os.path.join(path, d)
        if not os.path.exists(dir_path):
            subprocess.call(['mkdir', dir_path])

    for c in TEMPLATES['COLLECTIONS'].values():
        c_path = os.path.join(path, DIRS['TEMPLATES'], c)
        if not os.path.exists(c_path):
            subprocess.call(['touch', c_path])

    t_path = os.path.join(path, DIRS['TEMPLATES'], TEMPLATES['POST'])
    if not os.path.exists(t_path):
        subprocess.call(['touch', t_path])


def _initialize_site_dir(path):
    site_path = os.path.join(path, DIRS['SITE'])

    if not os.path.exists(site_path):
        subprocess.call(['mkdir', site_path])

    static_path = os.path.join(path, DIRS['STATIC'])
    site_static_path = os.path.join(site_path, 'static')
    subprocess.call(['cp', '-r', static_path, site_static_path])
    return site_path, site_static_path


def _remove_site_dir(path):
    site_path = os.path.join(path, DIRS['SITE'])
    subprocess.call(['rm', '-r', site_path]) 


def _read_config(path):
    file_path = os.path.join(path, CONFIG_FILE)
    with open(file_path, 'r') as f:
        return yaml.load(f.read())


def _sort_posts(path):
    def is_post_file(p):
        isfile = os.path.isfile(os.path.join(path, p))
        valid_filename = len(p.split('-')) == 4
        return isfile and valid_filename

    posts = [p for p in os.listdir(path) if is_post_file(p)]
    return reversed(sorted(posts))


def _write_perm_page(post, site_path, html):
    date_folder = os.path.join(site_path, post.publish_folder)
    if not os.path.exists(date_folder):
        subprocess.call(['mkdir', '-p', date_folder])

    with open(post.publish_path, 'w') as p:
        p.write(html)


def _write_page(post, site_path, html):
    page_path = os.path.join(site_path, post.filename)
    with open(page_path, 'w') as p:
        p.write(html)


def _process_post(post, config, site_path):
    layout = post.layout or TEMPLATES['POST']
    tmpl = JINJA_ENV.get_template(layout)
    html = tmpl.render(site=config, post=post)
    _write_perm_page(post, site_path, html)


def _process_page(post, config, site_path):
    layout = post.layout or TEMPLATES['PAGE']
    tmpl = JINJA_ENV.get_template(layout)
    html = tmpl.render(site=config, post=post)
    _write_page(post, site_path, html)


def _write_collection(path, template, config, posts):
    tmpl = JINJA_ENV.get_template(template)
    html = tmpl.render(site=config, posts=posts)
    with open(os.path.join(path, template), 'w') as index:
        index.write(html)


def init(path):
    _initialize_blog_dir(path)


def clean(path):
    _remove_site_dir(path)


def build(path):
    site_path, static_dir = _initialize_site_dir(path)
    config = _read_config(path)

    ps = _sort_posts(os.path.join(path, DIRS['POSTS']))
    posts = [Post(path, fname) for fname in ps]
    for post in posts:
        _process_post(post, config, site_path)

    pgs = os.listdir(os.path.join(path, DIRS['PAGES']))
    pages = [Page(path, fname) for fname in pgs]
    for page in pages:
        _process_page(page, config, site_path)

    for t in TEMPLATES['COLLECTIONS'].values():
        _write_collection(site_path, t, config, posts)


def main():
    args = docopt.docopt(__doc__, version=__version__)
    p = os.getcwd() if args['PATH'] is None else args['PATH']
    path = os.path.abspath(p)

    try:
        if args['init']:
            init(path)

        if args['clean']:
            clean(path)

        if args['build']:
            build(path)
    except Exception as e:
        print('Error: {}'.format(e))


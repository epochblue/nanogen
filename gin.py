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
from collections import OrderedDict

import yaml
import jinja2
import docopt
import markdown

__all__ = ['main']
__version__ = '0.1.0'
__author__ = 'Bill Israel <bill.israel@gmail.com>'

FILES = {
    'MANIFEST': 'manifest.yaml'
}

DIRS = {
    'POSTS': '_posts',
    'STATIC': '_static',
    'TEMPLATES': '_templates',
    'SITE': 'site'
}

TEMPLATE_PATH = os.path.join(os.path.abspath('.'), DIRS['TEMPLATES'])

JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_PATH))


class Post(object):
    """Represents a post."""
    def __init__(self, path, date, fname):
        self.site_path = os.path.join(path, 'site')
        self.file_path = os.path.join(path, '_posts', fname)

        if not os.path.exists(self.file_path):
            raise ValueError('Unable to locate file {}'.format(self.file_path))

        with open(self.file_path, 'r') as f: 
            file_str = f.read()
        
        split_file = file_str.split('----')
        self.front_matter = yaml.load(split_file[1])
        self.content = markdown.markdown(split_file[2].strip())
        self.publish_date = date

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


def _initialize_blog_dir(path):
    for f in FILES.values():
        file_path = os.path.join(path, f)
        if not os.path.exists(file_path):
            subprocess.call(['touch', f])

    for d in DIRS.values():
        dir_path = os.path.join(path, d)
        if not os.path.exists(dir_path):
            subprocess.call(['mkdir', d])


def _initialize_site_dir(path):
    site_path = os.path.join(path, DIRS['SITE'])

    if os.path.exists(site_path):
        subprocess.call(['rm', '-r', site_path])

    subprocess.call(['mkdir', site_path])

    static_path = os.path.join(path, '_static')
    site_static_path = os.path.join(path, 'site', 'static')
    subprocess.call(['cp', '-r', static_path, site_static_path])
    return site_path, site_static_path


def _remove_site_dir(path):
    site_path = os.path.join(path, DIRS['SITE'])
    subprocess.call(['rm', '-r', site_path]) 


def _read_manifest(path):
    file_path = os.path.join(path, FILES['MANIFEST'])
    with open(file_path, 'r') as f:
        return yaml.load(f.read())


def _sort_posts(posts):
    by_date = sorted(posts.items(), key=lambda t: t[0])
    rev_chrono = reversed(by_date)
    return OrderedDict(rev_chrono)


def _write_perm_page(post, site_path, html):
    year, month = post.publish_date.year, post.publish_date.month
    date_folder = os.path.join(site_path, '{}/{}'.format(year, month))
    if not os.path.exists(date_folder):
        subprocess.call(['mkdir', '-p', date_folder])

    with open(post.path, 'w') as p:
        p.write(html)


def _process_post(post, config, site_path):
    layout = post.front_matter.get('layout', None)
    if layout is None:
        raise ValueError('{} has no defined layout'.format(post.path))

    try:
        tmpl = JINJA_ENV.get_template(layout)
    except:
        raise ValueError('Unable to render template {}'.format(layout))

    html = tmpl.render(site=config, post=post)
    _write_perm_page(post, site_path, html)


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
    manifest = _read_manifest(path)
    config = manifest.get('config', {})
    ps = _sort_posts(manifest['posts'])
    posts = [Post(path, dt, fname) for dt, fname in ps.items()]

    for post in posts:
        _process_post(post, config, site_path)

    for t in ['index.html', 'archive.html', 'rss.xml']:
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


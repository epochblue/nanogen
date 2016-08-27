"""
nanogen - a very small blog generator
"""
import os
import re
import shutil
import datetime
import subprocess

import jinja2

import logger
import renderer


__author__ = 'Bill Israel <bill.israel@gmail.com>'
__version__ = (0, 9, 9)
version = '.'.join(map(str, __version__))


class Post(object):
    """Represents a post."""

    def __init__(self, base_path, path_to_file):
        logger.log.debug('Processing post at %s', path_to_file)
        self.base_path = base_path
        self.path = path_to_file
        self.filename = self.path.split('/')[-1]

        with open(self.path, 'r') as p:
            self.raw_content = p.read()

        self.title = self.raw_content.strip().splitlines()[0].lstrip('#')
        self.content = renderer.markdown(self.raw_content)

    def __repr__(self):
        return u'{}(path={})'.format(self.__class__.__name__, self.path)

    @property
    def pub_date(self):
        year, month, day = map(int, self.filename.split('-', 3)[:3])
        return datetime.datetime(year=year, month=month, day=day)

    @property
    def slug(self):
        return '-'.join(self.filename.split('-', 3)[3:]).rsplit('.', 1)[0]

    @property
    def html_filename(self):
        return '{}.html'.format(self.slug)

    @property
    def permapath(self):
        dt = self.pub_date
        return os.path.join(self.base_path, str(dt.year),
                            '{:02d}'.format(dt.month), self.html_filename)

    @property
    def permalink(self):
        dt = self.pub_date
        return '/{}/{:02d}/{}'.format(dt.year, dt.month, self.html_filename)


class Blog(object):
    PATHS = {
        'cwd': os.getcwd(),
        'site': os.path.join(os.getcwd(), '_site'),
        'posts': os.path.join(os.getcwd(), '_posts'),
        'layout': os.path.join(os.getcwd(), '_layout')
    }

    def __init__(self):
        self.posts = None

        jinja_loader = jinja2.FileSystemLoader(self.PATHS['layout'])
        self.jinja_env = jinja2.Environment(loader=jinja_loader)

    def slugify(self, text):
        """Create a suitable slug for the given text"""
        return re.sub(r'\W', '-', text).lower()

    def is_valid_post_file(self, path):
        """
        Determines if the given path is valid for a post file.

        The criteria:
            1. The file can't start with an underscore; these are ignored
            2. The file's name must match the pattern yyyy-mm-dd-*
            3. The file's extension must be a valid Markdown extension

        :param path: The file path to validate
        """
        post_pattern = r'^\d{4}-\d{2}-\d{2}-.*'
        markdown_extensions = ['md', 'markdown', 'mdown']

        filename, ext = os.path.basename(path).rsplit('.', 1)

        ignored = not filename.startswith('_')
        valid_filename = re.match(post_pattern, filename)
        valid_ext = ext in markdown_extensions

        return ignored and valid_filename and valid_ext

    def collect_posts(self):
        """
        Finds valid post files within the posts directory.

        :return: None
        """
        if self.posts is None:
            ls = os.listdir(self.PATHS['posts'])
            post_path = lambda path: os.path.join(self.PATHS['posts'], path)
            self.posts = [Post(self.PATHS['site'], post_path(p))
                          for p in ls
                          if self.is_valid_post_file(p)]
        return self.posts

    def generate_posts(self):
        """
        Looks for valid post files to process and processes them.

        :return: None
        """
        logger.log.debug('Processing posts...')
        posts = self.collect_posts()

        for post in posts:
            logger.log.debug('Rendering template for post %s', post.path)
            template = self.jinja_env.get_template('post.html')
            html = template.render(post=post)

            logger.log.debug('Writing post to disk: %s', post)
            post_dir = os.path.dirname(post.permapath)
            if not os.path.isdir(post_dir):
                logger.log.debug('Creating post directory %s', post_dir)
                subprocess.call(['mkdir', '-p', post_dir])

            logger.log.debug('Writing post to %s', post.permapath)
            with open(post.permapath, 'w') as pout:
                pout.write(html)

    def generate_index_pages(self):
        """
        Generate the index pages (list of posts, RSS feed).

        :return: None
        """
        logger.log.debug('Writing index pages...')
        posts = self.collect_posts()

        for page in ('index.html', 'rss.xml'):
            logger.log.debug('Rendering template for page %s', page)
            filepath = os.path.join(self.PATHS['site'], page)
            template = self.jinja_env.get_template(page)
            html = template.render(posts=list(reversed(posts)))

            logger.log.debug('Writing page to disk: %s', page)
            with open(filepath, 'w') as pout:
                pout.write(html)

    def copy_static_files(self):
        """
        Copy static files into the _sites directory.

        :return: None
        """
        shutil.copytree(os.path.join(self.PATHS['layout'], 'static'),
                        os.path.join(self.PATHS['site'], 'static'))

    def init(self):
        """
        Initialize the current directory for a nanogen-based site.

        :return: None
        """
        for d in [self.PATHS['posts'], self.PATHS['templates']]:
            logger.log.debug('Creating directory %s' % d)
            if not os.path.isdir(d):
                subprocess.call(['mkdir', d])

    def build(self):
        """
        Generate the site. Will create the _site dir if one doesn't already exist.

        :return: None
        """
        if not os.path.isdir(self.PATHS['site']):
            logger.log.debug('Creating site directory...')
            subprocess.call(['mkdir', self.PATHS['site']])

        self.generate_posts()
        self.generate_index_pages()
        self.copy_static_files()

    def clean(self):
        """
        Removes all generated nanogen files.

        :return: None
        """
        logger.log.info('Cleaning generated files...')
        site_dir = self.PATHS['site']
        if os.path.isdir(site_dir):
            subprocess.call(['rm', '-r', site_dir])

    def new(self, title):
        """
        Creates a new post for the site.

        :param title: What to use as the title for this post
        :type title: string
        :raises: ValueError if this post already exists
        :return: None
        """
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        slug = self.slugify(title)
        filename = '{}-{}.md'.format(date, slug)
        full_path = os.path.join(self.PATHS['posts'], filename)

        default_post = """
## {title}

Your post content goes here.
""".strip()

        if not os.path.isfile(full_path):
            with open(full_path, 'w') as f:
                text = default_post.format(title=title)
                f.write(text)
            logger.log.info('Created {file}'.format(file=full_path))
        else:
            raise ValueError('A post with that date and title already exists')

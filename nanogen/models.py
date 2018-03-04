"""
nanogen - a very small blog generator
"""
import datetime
import os
import shutil
import subprocess
import textwrap

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import jinja2

from nanogen import logger
from nanogen import renderer
from nanogen import utils


__author__ = 'Bill Israel <bill.israel@gmail.com>'


class Post(object):
    """Represents a post."""

    def __init__(self, base_path, path_to_file):
        logger.log.debug('Processing post at %s', path_to_file)
        self.base_path = base_path
        self.path = path_to_file
        self.filename = self.path.split('/')[-1]

        with open(self.path, 'r') as p:
            self.raw_content = p.read()

        lines = self.raw_content.strip().splitlines()
        self.title = lines[0].lstrip('#').strip()
        self.markdown_content = '\n'.join(lines[2:]).strip()
        self.html_content = renderer.markdown(self.markdown_content)

    def __repr__(self):
        return u'{}(base_path={}, path_to_file={})'.format(
            self.__class__.__name__,
            self.base_path,
            self.path
        )

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
        return os.path.join(str(dt.year), '{:02d}'.format(dt.month), self.html_filename)


class Blog(object):
    def __init__(self, base_dir):
        self.PATHS = {
            'cwd': base_dir,
            'site': os.path.join(base_dir, '_site'),
            'posts': os.path.join(base_dir, '_posts'),
            'drafts': os.path.join(base_dir, '_drafts'),
            'layout': os.path.join(base_dir, '_layout')
        }
        
        self.config = self.parse_config()
        self.posts = self.collect_posts()

        jinja_loader = jinja2.FileSystemLoader(self.PATHS['layout'])
        self.jinja_env = jinja2.Environment(loader=jinja_loader)

    def parse_config(self):
        """
        Pulls in high-level config variables about the blog.

        :return: A dictionary of configuration items
        :rtype: dict
        """
        config = configparser.ConfigParser()
        config.read(os.path.join(self.PATHS['cwd'], 'blog.cfg'))
        return config

    def collect_posts(self):
        """
        Finds valid post files within the posts directory.

        :return: A list of found posts
        :rtype: list
        """
        if not os.path.isdir(self.PATHS['posts']):
            # There are no posts yet, so let's get outta here
            return []

        ls = os.listdir(self.PATHS['posts'])
        post_path = lambda path: os.path.join(self.PATHS['posts'], path)
        return [Post(self.PATHS['site'], post_path(p))
                for p in ls
                if utils.is_valid_post_file(p)]

    def generate_posts(self):
        """
        Looks for valid post files to process and processes them.

        :return: None
        """
        logger.log.debug('Processing posts...')

        for post in self.posts:
            logger.log.debug('Rendering template for post %s', post.path)
            template = self.jinja_env.get_template('post.html')
            html = template.render(site=self.config['site'], post=post)

            logger.log.debug('Writing post to disk: %s', post)
            post_dir = os.path.dirname(post.permapath)
            if not os.path.isdir(post_dir):
                logger.log.debug('Creating post directory %s', post_dir)
                subprocess.call(['mkdir', '-p', post_dir])

            logger.log.debug('Writing post to %s', post.permapath)
            with open(post.permapath, 'w') as pout:
                pout.write(html)

    def generate_index_page(self):
        """
        Generate the index page of posts.

        :return: None
        """
        logger.log.debug('Writing index page...')
        posts = self.posts

        logger.log.debug('Rendering index.html')
        filepath = os.path.join(self.PATHS['site'], 'index.html')
        template = self.jinja_env.get_template('index.html')
        html = template.render(site=self.config['site'], posts=list(reversed(posts)))

        logger.log.debug('Writing page to disk: index.html')
        with open(filepath, 'w') as pout:
            pout.write(html)

    def generate_feeds(self):
        logger.log.debug('Writing feed pages...')
        posts = self.posts

        for feed in ('rss.xml', 'feed.json'):
            logger.log.debug('Rendering index.html')
            filepath = os.path.join(self.PATHS['site'], feed)

            try:
                template = self.jinja_env.get_template(feed)
            except jinja2.TemplateNotFound:
                logger.log.debug('Unable to locate template for %s, skipping...', feed)
                continue

            html = template.render(site=self.config['site'], posts=list(reversed(posts)))

            logger.log.debug('Writing page to disk: %s', feed)
            with open(filepath, 'w') as pout:
                pout.write(html)

    def copy_static_files(self):
        """
        Copy static files into the _sites directory.

        :return: None
        """
        layout_static = os.path.join(self.PATHS['layout'], 'static')
        site_static = os.path.join(self.PATHS['site'], 'static')

        if os.path.isdir(os.path.join(site_static)):
            shutil.rmtree(site_static)

        shutil.copytree(layout_static, site_static)

    def init(self):
        """
        Initialize the current directory for a nanogen-based site.

        :return: None
        """
        for d in (self.PATHS['posts'], self.PATHS['layout'], self.PATHS['drafts']):
            logger.log.debug('Creating directory %s' % d)
            if not os.path.isdir(d):
                subprocess.call(['mkdir', d])

        # Generate template blog configuration file
        config_path = os.path.join(self.PATHS['cwd'], 'blog.cfg')
        if not os.path.exists(config_path):
            with open(config_path, 'w') as f:
                text = textwrap.dedent("""\
                [site]
                title = Your blog's title here
                author = Your name here
                email = you@wherever.com
                url = https://yourblog.example.com
                description = Your blog's description here
                """)
                f.write(text)

    def build(self):
        """
        Generate the site. Will create the _site dir if one doesn't already exist.

        :return: None
        """
        if not os.path.isdir(self.PATHS['site']):
            logger.log.debug('Creating site directory...')
            subprocess.call(['mkdir', self.PATHS['site']])

        self.generate_posts()
        self.generate_index_page()
        self.generate_feeds()
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

    def new_post(self, title, draft=False):
        """
        Creates a new post for the site.

        :param title: What to use as the title for this post
        :type title: string
        :param draft: Indicates where the file being created is a draft
        :type draft: bool
        :raises: ValueError if this post already exists
        :return: None
        """
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        slug = utils.slugify(title)
        filename = '{}-{}.md'.format(date, slug)
        base_path = self.PATHS['drafts'] if draft else self.PATHS['posts']
        full_path = os.path.join(base_path, filename)

        default_post = textwrap.dedent("""\
        ## {title}

        Your post content goes here.
        """)

        if os.path.isfile(full_path):
            raise ValueError('A post with that date and title already exists')

        with open(full_path, 'w') as f:
            text = default_post.format(title=title)
            f.write(text)
        logger.log.info('Created {file}'.format(file=full_path))

        # Open your new post in $VISUAL or $EDITOR or fallback to `nano`
        editor = os.environ.get('VISUAL', os.environ.get('EDITOR', 'nano'))
        subprocess.call([editor, full_path])

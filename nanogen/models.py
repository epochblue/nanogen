"""
nanogen - a very small blog generator
"""
import datetime
import json
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
    def __init__(self, base_dir, is_preview=False):
        self.PATHS = {
            'cwd': base_dir,
            'site': os.path.join(base_dir, '_site'),
            'preview': os.path.join(base_dir, '_preview'),
            'posts': os.path.join(base_dir, '_posts'),
            'drafts': os.path.join(base_dir, '_drafts'),
            'layout': os.path.join(base_dir, '_layout')
        }
        
        self.config = self.parse_config()
        self.output_dir = self.PATHS['preview'] if is_preview else self.PATHS['site']
        self.posts = self.collect_posts(include_drafts=is_preview)

        jinja_loader = jinja2.FileSystemLoader(self.PATHS['layout'])
        self.jinja_env = jinja2.Environment(loader=jinja_loader)
        self.jinja_env.filters['to_json'] = json.dumps

    def parse_config(self):
        """
        Pulls in high-level config variables about the blog.

        :return: A dictionary of configuration items
        :rtype: dict
        """
        config = configparser.ConfigParser()
        config.read(os.path.join(self.PATHS['cwd'], 'blog.cfg'))
        return config

    def collect_posts(self, include_drafts=False):
        """
        Finds valid post files within the posts directory.

        :param include_drafts: True if draft posts should be included
        :type include_drafts: bool
        :return: A list of found posts
        :rtype: list
        """
        if not os.path.isdir(self.PATHS['posts']):
            # There are no posts yet, so let's get outta here
            return []

        ls = os.listdir(self.PATHS['posts'])
        post_path = lambda path: os.path.join(self.PATHS['posts'], path)
        posts = [Post(self.output_dir, post_path(p))
                 for p in ls
                 if utils.is_valid_post_file(p)]

        if include_drafts:
            ls = os.listdir(self.PATHS['drafts'])
            drafts_path = lambda path: os.path.join(self.PATHS['drafts'], path)
            posts.extend([Post(self.output_dir, drafts_path(p))
                          for p in ls
                          if utils.is_valid_post_file(p)])
        return posts

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
        output_file = os.path.join(self.output_dir, 'index.html')
        template = self.jinja_env.get_template('index.html')
        html = template.render(site=self.config['site'], posts=list(reversed(posts)))

        logger.log.debug('Writing page to disk: index.html')
        with open(output_file, 'w') as pout:
            pout.write(html)

    def generate_feeds(self):
        """
        Generate RSS and JSON feed files, if templates for them exist.

        :return: None
        """
        logger.log.debug('Writing feed pages...')
        posts = self.posts

        for feed in ('rss.xml', 'feed.json'):
            logger.log.debug('Rendering index.html')
            output_file = os.path.join(self.output_dir, feed)

            try:
                template = self.jinja_env.get_template(feed)
            except jinja2.TemplateNotFound:
                logger.log.debug('Unable to locate template for %s, skipping...', feed)
                continue

            html = template.render(site=self.config['site'], posts=list(reversed(posts)))

            logger.log.debug('Writing page to disk: %s', feed)
            with open(output_file, 'w') as pout:
                pout.write(html)

    def copy_static_files(self):
        """
        Copy static files into the output directory.

        :return: None
        """
        layout_static = os.path.join(self.PATHS['layout'], 'static')
        output_static = os.path.join(self.output_dir, 'static')

        if not os.path.isdir(layout_static):
            return

        if os.path.isdir(os.path.join(output_static)):
            shutil.rmtree(output_static)

        shutil.copytree(layout_static, output_static)

    def init(self):
        """
        Initialize the current directory for a nanogen-based site.

        :return: None
        """
        current_dir = self.PATHS['cwd']
        parent_dir = os.path.dirname(__file__)
        template_dir = os.path.join(parent_dir, 'template')
        for item in os.listdir(template_dir):
            source = os.path.join(template_dir, item)
            dest = os.path.join(current_dir, item)

            if os.path.exists(dest):
                continue

            ignored_names = lambda src, names: [n for n in names if n.startswith('.')]
            if os.path.isdir(source):
                shutil.copytree(source, dest, ignore=ignored_names)
            else:
                shutil.copy2(source, dest)

    def build(self):
        """
        Generate the site. Will create the output dir if necessary.

        :return: None
        """
        if not os.path.isdir(self.output_dir):
            logger.log.debug('Creating output directory...')
            subprocess.call(['mkdir', self.output_dir])

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
        if os.path.isdir(self.output_dir):
            subprocess.call(['rm', '-r', self.output_dir])

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

    def publish(self, filename):
        """
        Publishes a post currently in draft by moving it from the drafts
        folder to the posts folder, and updating its date to today's date (the
        date of "publication").

        :param filename: The filename of the draft being published
        :type filename: str
        :return: None
        """
        drafts_dir = self.PATHS['drafts']
        posts_dir = self.PATHS['posts']
        filename_with_ext = os.path.basename(filename)

        drafts = os.listdir(drafts_dir)
        if filename_with_ext not in drafts:
            raise ValueError('Unable to locate {} in drafts'.format(filename))

        filename, ext = filename_with_ext.rsplit('.', 1)

        today = datetime.date.today()
        filename_parts = filename.split('-', 3)
        post_filename = '{year}-{month:02d}-{day:02d}-{slug}.{ext}'.format(
            year=today.year,
            month=today.month,
            day=today.day,
            slug=filename_parts[-1],
            ext=ext
        )

        os.rename(
            os.path.join(drafts_dir, filename_with_ext),
            os.path.join(posts_dir, post_filename)
        )

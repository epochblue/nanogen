import os
import yaml
import datetime

import renderer
from . import PATHS
from logger import log

FM_SEPARATOR = '----'


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
        return u'Post(path={})'.format(self.path)

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

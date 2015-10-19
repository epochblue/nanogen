import os
import re

__version__ = '0.8.0'

PATHS = {
    'cwd': os.getcwd(),
    'site': os.path.join(os.getcwd(), '_site'),
    'posts': os.path.join(os.getcwd(), '_posts'),
    'layouts': os.path.join(os.getcwd(), '_layouts'),
}


def slugify(text):
    """Create a suitable slug for the given text"""
    return re.sub(r'\W', '-', text).lower()

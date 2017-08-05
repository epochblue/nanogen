import os
import re


def slugify(text):
    """Create a suitable slug for the given text"""
    return re.sub(r'\W', '-', text).lower()


def is_valid_post_file(path):
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

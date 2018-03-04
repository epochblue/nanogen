import os
import re


def slugify(text):
    """Create a good-enough slug for the given text"""
    return re.sub(r'\W', '-', text).lower()


def is_valid_post_file(basename):
    """
    Determines if the given filename is valid for a post file.

    The criteria:
        1. The file can't start with an underscore; these are ignored
        2. The file's name must match the pattern yyyy-mm-dd-*
        3. The file's extension must be a valid Markdown extension

    :param basename: The file name to validate
    :type basename: string
    """
    post_pattern = r'^\d{4}-\d{2}-\d{2}-.*'
    markdown_extensions = ['md', 'markdown', 'mdown']

    if '.' not in basename:
        return False

    filename, ext = os.path.basename(basename).rsplit('.', 1)

    ignorable = filename.startswith('_')
    valid_filename = re.match(post_pattern, filename)
    valid_extension = ext in markdown_extensions

    return not ignorable and valid_filename and valid_extension

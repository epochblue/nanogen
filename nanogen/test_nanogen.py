import os
import tempfile
import datetime

from .nanogen import _slugify, _is_valid_post_file, Post


def test_slugify():
    assert _slugify('This is a test string') == 'this-is-a-test-string'
    assert _slugify('Another test!') == 'another-test-'
    assert _slugify('lorem-ipsum-blah') == 'lorem-ipsum-blah'


def test_is_valid_post_file():
    # Valid cases
    assert _is_valid_post_file('/path/to/2015-10-22-example-title.md')
    assert _is_valid_post_file('/path/to/2015-10-22-example-title.mdown')
    assert _is_valid_post_file('/path/to/2015-10-22-example-title.markdown')
    assert not _is_valid_post_file('/path/to/_2015-10-22-example-title.markdown')

    # Invalid cases
    assert not _is_valid_post_file('/path/to/15-10-22-example-title.md')
    assert not _is_valid_post_file('/path/to/2015-10-22-example-title.html')


def test_post_creation():
    filename = '2015-10-22-test-post.md'
    path = os.path.join(tempfile.gettempdir(), filename)

    with open(path, 'w') as f:
        f.write("""
----
title: Lorem Ipsum
slug: lorem-ipsum
layout: post.html
----

## Lorem Ipsum

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas pretium
consequat diam, ac feugiat lorem dapibus egestas. Phasellus mattis scelerisque
nunc et ultricies. Ut facilisis lectus vel mi pharetra, lobortis laoreet erat
dictum. Aliquam vehicula tellus nec velit porttitor aliquet.
        """)

    p = Post(path)

    assert p.title == 'Lorem Ipsum'
    assert p.slug == 'lorem-ipsum'
    assert p.layout == 'post.html'
    assert p.content == """<h2>Lorem Ipsum</h2>
<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas pretium
consequat diam, ac feugiat lorem dapibus egestas. Phasellus mattis scelerisque
nunc et ultricies. Ut facilisis lectus vel mi pharetra, lobortis laoreet erat
dictum. Aliquam vehicula tellus nec velit porttitor aliquet.</p>
"""
    assert p.pub_date == datetime.datetime(year=2015, month=10, day=22)
    assert p.html_filename == 'lorem-ipsum.html'
    assert p.permapath == os.path.join(os.getcwd(), '_site', '2015', '10', 'lorem-ipsum.html')
    assert p.permalink == '/2015/10/lorem-ipsum.html'


def test_post_creation_defaults():
    filename = '2015-10-22-test-post.md'
    path = os.path.join(tempfile.gettempdir(), filename)

    with open(path, 'w') as f:
        f.write("""
title: Lorem Ipsum
----

## Lorem Ipsum

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas pretium
consequat diam, ac feugiat lorem dapibus egestas. Phasellus mattis scelerisque
nunc et ultricies. Ut facilisis lectus vel mi pharetra, lobortis laoreet erat
dictum. Aliquam vehicula tellus nec velit porttitor aliquet.
        """)

    p = Post(path)

    assert p.slug == 'test-post'
    assert p.layout is None
    assert p.pub_date == datetime.datetime(year=2015, month=10, day=22)
    assert p.html_filename == 'test-post.html'
    assert p.permapath == os.path.join(os.getcwd(), '_site', '2015', '10', 'test-post.html')
    assert p.permalink == '/2015/10/test-post.html'

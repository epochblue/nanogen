import datetime
import os
from unittest import mock

from nanogen import models


example_post = """\
# Test Post

And this is my _markdown_ **content**.

Look, it also has:

* an
* unordered
* list
"""

example_config = """\
[site]
author = Example user
email = user@example.com
description = A test description
url = http://www.example.com
title = Test Example
"""


def test_post(tmpdir):
    f = tmpdir.mkdir('blog').join('2018-01-01-test-post.md')
    f.write(example_post)

    file_path = os.path.join(str(tmpdir), 'blog', '2018-01-01-test-post.md')
    p = models.Post(str(tmpdir), file_path)

    assert p.filename == '2018-01-01-test-post.md'
    assert p.title == 'Test Post'
    assert p.raw_content == example_post
    expected_markdown = example_post.strip().splitlines()
    assert p.markdown_content == '\n'.join(expected_markdown[2:])
    assert p.pub_date == datetime.datetime(2018, 1, 1, 0, 0, 0)
    assert p.slug == 'test-post'
    assert p.html_filename == 'test-post.html'
    assert p.permapath == os.path.join(str(tmpdir), '2018', '01', 'test-post.html')
    assert p.permalink == os.path.join('2018', '01', 'test-post.html')


def test_blog_create(tmpdir):
    path = tmpdir.mkdir('blog')
    config_file = path.join('blog.cfg')
    config_file.write(example_config)
    blog = models.Blog(str(path))
    assert len(blog.posts) == 0
    assert blog.config['site']['author'] == 'Example user'
    assert blog.config['site']['email'] == 'user@example.com'
    assert blog.config['site']['description'] == 'A test description'
    assert blog.config['site']['url'] == 'http://www.example.com'
    assert blog.config['site']['title'] == 'Test Example'


def test_blog_init(tmpdir):
    path = tmpdir.mkdir('blog')
    blog = models.Blog(str(path))
    blog.init()

    listing = [os.path.basename(str(file)) for file in path.listdir()]
    assert len(listing) == 4
    assert 'blog.cfg' in listing
    assert '_layout' in listing
    assert '_posts' in listing
    assert '_drafts' in listing


def test_blog_new_post(tmpdir):
    path = tmpdir.mkdir('blog')
    blog = models.Blog(str(path))
    blog.init()

    before_posts = blog.collect_posts()
    assert len(before_posts) == 0

    with mock.patch('subprocess.call'):
        blog.new_post('Test title', draft=False)

    after_posts = blog.collect_posts()
    assert len(after_posts) == 1
    today = datetime.date.today()
    expected_filename = '{}-{:02d}-{:02d}-test-title.md'.format(
        today.year,
        today.month,
        today.day
    )
    assert after_posts[0].filename == expected_filename


def test_blog_new_draft(tmpdir):
    path = tmpdir.mkdir('blog')
    blog = models.Blog(str(path))
    blog.init()

    before_posts = blog.collect_posts()
    assert len(before_posts) == 0

    with mock.patch('subprocess.call'):
        blog.new_post('Test title', draft=True)

    after_posts = blog.collect_posts()
    assert len(after_posts) == 0


def test_blog_copy_static_files(tmpdir):
    path = tmpdir.mkdir('blog')
    site_path = path.mkdir('_site')

    # Add a static file to the projet
    blog = models.Blog(str(path))
    blog.init()
    blog.copy_static_files()

    site_static_path = site_path.join('static')
    static_files = [os.path.basename(str(file)) for file in site_static_path.listdir()]
    assert 'blog.css' in static_files


def test_blog_generate_posts(tmpdir):
    path = tmpdir.mkdir('blog')
    site_path = path.mkdir('_site')

    # Set up a nanogen blog for posts
    blog = models.Blog(str(path))
    blog.init()

    with mock.patch('subprocess.call'):
        blog.new_post('Test title 1', draft=False)

    post_template = path.join('_layout').join('post.html')
    post_template.write("""\
    <!doctype html>
    <html>
    <body>Single post template would go here.</body>
    </html>
    """)

    # Refresh the blog instance to better emulate real-world usage
    blog = models.Blog(str(path))
    blog.generate_posts()

    today = datetime.date.today()
    expected_post_dir = site_path.join('{}'.format(today.year)).join('{:02d}'.format(today.month))
    generated_posts = [os.path.basename(str(file)) for file in expected_post_dir.listdir()]
    assert len(generated_posts) == 1
    assert 'test-title-1.html' in generated_posts


def test_blog_generate_index_page(tmpdir):
    path = tmpdir.mkdir('blog')
    site_path = path.mkdir('_site')

    # Set up a nanogen blog for posts
    blog = models.Blog(str(path))
    blog.init()

    with mock.patch('subprocess.call'):
        blog.new_post('Test title 1', draft=False)

    # Refresh the blog instance to better emulate real-world usage
    blog = models.Blog(str(path))
    blog.generate_index_page()

    site_dir = [os.path.basename(str(file)) for file in site_path.listdir()]
    assert 'index.html' in site_dir


def test_blog_generate_feeds_no_feed_files(tmpdir):
    path = tmpdir.mkdir('blog')
    site_path = path.mkdir('_site')

    # Set up a nanogen blog for posts
    blog = models.Blog(str(path))
    blog.init()

    # Remove the feed files
    os.unlink(os.path.join(blog.PATHS['layout'], 'rss.xml'))
    os.unlink(os.path.join(blog.PATHS['layout'], 'feed.json'))

    # Refresh the blog instance to better emulate real-world usage
    blog = models.Blog(str(path))
    blog.generate_feeds()

    site_dir = [os.path.basename(str(file)) for file in site_path.listdir()]
    assert 'rss.xml' not in site_dir
    assert 'feed.json' not in site_dir


def test_blog_feeds(tmpdir):
    path = tmpdir.mkdir('blog')
    site_path = path.mkdir('_site')

    # Set up a nanogen blog for posts
    blog = models.Blog(str(path))
    blog.init()

    with mock.patch('subprocess.call'):
        blog.new_post('Test title 1', draft=False)

    # Refresh the blog instance to better emulate real-world usage
    blog = models.Blog(str(path))
    blog.generate_feeds()

    site_dir = [os.path.basename(str(file)) for file in site_path.listdir()]
    assert 'rss.xml' in site_dir
    assert 'feed.json' in site_dir


def test_blog_build_and_clean(tmpdir):
    path = tmpdir.mkdir('blog')
    site_path = path.mkdir('_site')

    # Set up a nanogen blog for posts
    blog = models.Blog(str(path))
    blog.init()

    with mock.patch('subprocess.call'):
        blog.new_post('Test title 1', draft=False)

    post_template = path.join('_layout').join('post.html')
    post_template.write("""\
    <!doctype html>
    <html>
    <body>Post template would go here.</body>
    </html>
    """)

    index_template = path.join('_layout').join('index.html')
    index_template.write("""\
    <!doctype html>
    <html>
    <body>Index template would go here.</body>
    </html>
    """)

    blog_config = path.join('_layout').join('blog.cfg')
    blog_config.write(example_config)

    # Refresh the blog instance to better emulate real-world usage
    blog = models.Blog(str(path))
    blog.build()

    site_dir = [os.path.basename(str(file)) for file in site_path.listdir()]
    assert 'index.html' in site_dir

    today = datetime.date.today()
    expected_post_dir = site_path.join('{}'.format(today.year)).join('{:02d}'.format(today.month))
    generated_posts = [os.path.basename(str(file)) for file in expected_post_dir.listdir()]
    assert len(generated_posts) == 1
    assert 'test-title-1.html' in generated_posts

    blog.clean()
    assert not os.path.isdir(str(site_path))


def test_blog_build_and_clean_with_drafts(tmpdir):
    path = tmpdir.mkdir('blog')
    preview_path = path.mkdir('_preview')

    # Set up a nanogen blog for posts
    blog = models.Blog(str(path))
    blog.init()

    with mock.patch('subprocess.call'):
        blog.new_post('Test post', draft=False)
        blog.new_post('Draft post', draft=True)

    post_template = path.join('_layout').join('post.html')
    post_template.write("""\
    <!doctype html>
    <html>
    <body>Post template would go here.</body>
    </html>
    """)

    index_template = path.join('_layout').join('index.html')
    index_template.write("""\
    <!doctype html>
    <html>
    <body>Index template would go here.</body>
    </html>
    """)

    blog_config = path.join('_layout').join('blog.cfg')
    blog_config.write(example_config)

    # Refresh the blog instance to better emulate real-world usage
    blog = models.Blog(str(path), is_preview=True)
    blog.build()

    site_dir = [os.path.basename(str(file)) for file in preview_path.listdir()]
    assert 'index.html' in site_dir

    today = datetime.date.today()
    expected_post_dir = preview_path.join('{}'.format(today.year)).join('{:02d}'.format(today.month))
    generated_posts = [os.path.basename(str(file)) for file in expected_post_dir.listdir()]
    assert len(generated_posts) == 2
    assert 'test-post.html' in generated_posts
    assert 'draft-post.html' in generated_posts

    blog.clean()
    assert not os.path.isdir(str(preview_path))

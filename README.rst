nanogen
#######

A very small static blog generator written in Python.

.. image:: https://img.shields.io/pypi/v/nanogen.svg
    :target: https://pypi.python.org/pypi/nanogen
    :alt: Latest PyPI version

Purpose
=======

``nanogen`` exists solely so I can have a blogging platform I call my own.
The platform is very intentionally bare bones and simple. The code is
intentionally utilitarian and realistically less-than-perfect.

If you have an idea for a way to improve this without significantly increasing
``nanogen``'s complexity, please open an issue and let me know.

If you're looking for a more fully-featured static site generator, may I
recommend something like `Jekyll`_ or `Pelican`_ ?


Installation
============

The best way to install ``nanogen`` is through ``pip``::

    $> pip install nanogen


If you don't want to install it via ``pip``, you can install it
manually::

    $> git clone https://github.com/epochblue/nanogen
    $> cd nanogen
    $> python setup.py install


Note : To avoid possible dependency version issues, I recommend installing
``nanogen`` into a virtual environment, rather than globally.



How To Use
==========

Initializing
------------

Once ``nanogen`` is installed, navigate to the directory you'd like to
use as your new blog. Our examples will use a ``blog`` directory in ``$HOME``::

    $> mkdir blog
    $> cd blog

Once there, run ``nanogen``'s ``init`` command to get started::

    $> nanogen init

Running this command will generate the basic directories used by
``nanogen``. When this command completes, the ``blog`` directory will
look like this::

    ~/blog
    |-- _layout
    |   `-- blog.cfg
    `-- _posts

``_posts`` and ``_layout`` are the only two folders required by ``nanogen``, and
their names cannot be changed by the user. Your individual posts will go in the
``_posts`` directory, and the templates will go in the ``_layouts`` directory.

The ``blog.cfg`` file will hold metadata about your blog (author's name and
email, along with the site's title, description, and URL). A skeleton version of
this file is created for your during ``init``. The keys and values contained in
this file will be passed to your templates under the ``site`` variable. For
example: your site's title will be be available in the ``site.title`` attribute.

At this time, ``nanogen`` does not come with a built-in theme, so it's up to
you to create your own.


Creating Posts
--------------

One way to create new posts is by creating a new file in the ``_posts``
directory. The filename is important and must match the following rules:

1.  The file can't start with an underscore (they are ignored)
2.  The file's name must match the pattern ``yyyy-mm-dd-<post_title_slug>``
3.  The file's extension must be a valid Markdown extension (``md``, ``mdown``, or ``markdown``).

To illustrate::

    # valid filename
    2015-11-01-this-charming-man.md

    # invalid filename
    15-11-1-bigmouth-strikes-again.txt

If you don't want to try to remember all that, you can use ``nanogen``'s ``new``
command to do it for you. The only required argument to this command is the title of the
post being generated::

    $> nanogen new "Example Post Title"

Running this will create a properly-named and formatted file in the ``_posts``
directory.

Draft posts aren't an "official" feature of ``nanogen``, however they are
possible. By default, when ``nanogen`` generates a site it will only look in the
``_posts`` folder for files to process. If you'd like to maintain drafts of your
posts before you publish them, you can create a ``_drafts`` folder next to the
``_posts`` folder and ``nanogen`` will ignore it during site generation.
Alternatively, you can prepend the filename of a draft post with an underscore,
and ``nanogen`` will skip over it when searching for files to process.


Post Content Format
~~~~~~~~~~~~~~~~~~~

``nanogen`` posts don't use `YAML`_ front-matter, so the first line of your post
will be used for the title of the post. The content of the posts will be
processed as `Markdown`_ (the Github-flavored variety, complete with
syntax-highlighted code blocks). A minimal example of a valid ``nanogen`` post
is this::

    ## This will become the title (with hashes stripped out)

    **This** will become the post's _content_.

The title will be stripped out of the post's content, though it will be
available to your themes via the ``post.title`` attribute.


Generating Your Site
--------------------

Once you're ready to generate your site, you can use the ``build``
command::

    $> nanogen build

This command will walk your ``_posts`` directory, process any valid files it
finds, and will write all the generated HTML files into a ``_site`` folder.
Although you will want to preview this on your local development
system (see the following section for how to do this), the ``_site``
folder can be uploaded to your web host as-is.


Previewing Your Site
--------------------

To see what your site will look like *before* you upload it to a live
webserver for the world to see, ``nanogen`` provides a built-in server
that allows you to preview your generated site::

    $> nanogen preview

This command will start a server that listens on ``localhost`` port
``8080``. Simply open ``http://localhost:8080`` in a web broswer to
see how your site looks. If you'd like to use a different hostname or
port, ``nanogen`` provides an option for each (``-h|--host, and
-p|--port``, respectively). The following example will start a server
that listens on ``local.dev`` port ``8000`` (http://local.dev:8000)::

    $> nanogen preview --host local.dev --port 8000


Cleaning
--------

If your ``_site`` folder somehow gets corrupted, or you'd simply like
to generate your site from scratch, you can use the ``clean`` command::

    $> nanogen clean

There is no undo or confirmation when running this command.


``nanogen`` Themes
==================

*Note*: ``nanogen`` doesn't provide any themes out of the box. If you'd like to
develop your own theme for ``nanogen``, this section should explain how.

``nanogen`` uses `Jinja2`_ for its templating. If you need information
about Jinja's syntax, please `refer to their documentation
<http://jinja.pocoo.org/docs/>`_.


Template Files
--------------

The templates that make up the theme for your ``nanogen`` blog need to be placed
in the ``_layout`` directory. ``nanogen`` only expects a few files to exist, and
those files are:

1. ``index.html``
2. ``post.html``
3. ``rss.xml``

``index.html`` will be used as the sites homepage, ``post.html`` will be used to
generate each individual post, and ``rss.xml`` will be be used to generate your
blog's RSS feed.

All of your blog's posts will be passed to ``index.html`` and ``rss.xml`` via a
`Jinja2`_ context variable named ``posts`` (posts will be in reverse
chronological order). Individual posts will be passed to ``post.html`` via a
context variable named ``post``. Each post will have the following relevant
attributes available to use in the template:

* ``html_content`` - the HTML version of the post
* ``markdown_content`` - the Markdown version of the post (minus the title)
* ``title`` - the title of the post (will not be processed as Markdown)
* ``pub_date`` - a Python datetime object representing the publish date of the post
* ``permalink`` - the relative URL to the post

Please see the ``_layout`` directory in the included example for a basic theme
you can use to as a jumping off point for your own theme.


Static Files
------------

If you have any files that you'd like to include in the published site
(JavaScript files, CSS files, images, etc), place them into a folder named
``static`` inside the ``_layout`` folder. This folder will automatically be
copied into the ``_site`` folder during the build process. No processing will
be performed on the files within the ``static`` directory.


Sites Using ``nanogen``
=======================

* `http://blog.cubicle17.com/`__ (code is `available here`__)


License
#######

``nanogen`` is MIT licensed. Please see included ``LICENSE`` file for
more information.


Author
######

`Bill Israel`_ - `bill.israel@gmail.com`_


.. _Jekyll: http://jekyllrb.com
.. _Pelican: http://blog.getpelican.com
.. _Markdown: http://daringfireball.net/projects/markdown
.. _YAML: http://yaml.org/
.. _Jinja2: http://jinja2.pocoo.org/
.. _Bill Israel: http://billisrael.info/
.. _bill.israel@gmail.com: mailto:bill.israel@gmail.com

__ http://blog.cubicle17.com/
__ https://github.com/epochblue/blog

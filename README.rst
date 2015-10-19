nanogen
#######

A very small static site generator written in Python.

.. image:: https://img.shields.io/pypi/v/nanogen.svg
    :target: https://pypi.python.org/pypi/nanogen
    :alt: Latest PyPI version


Installation
============

The best way to install ``nanogen`` is through ``pip``::

    $> pip install nanogen


If you don't want to install it via ``pip``, you can install it
manually::

    $> git clone https://github.com/epochblue/nanogen
    $> cd nanogen
    $> python setup.py install


Note : To avoid possible dependency version issues, I advise installing
``nanogen`` into a virtual environment, rather than globally.



How To Use
==========

Initializing
------------

Once ``nanogen`` is installed, navigate to the directory you'd like to
use as your new blog. Our examples will use a ``blog`` directory in our
home directory::

    $> mkdir blog
    $> cd blog

Once there, run ``nanogen``'s ``init`` command to get started::

    $> nanogen init

Running this command will generate the basic directories used by
``nanogen``. When this command completes, the ``blog`` directory will
look like this::

    ~/blog
    |-- _posts
    `-- _layouts

These are all the only two folders required by ``nanogen``, and cannot
currently be changed by the user. If you're creating a blog-style
site, your individual posts will go in the ``_posts`` directory, and
your site's templates will go in the ``_layouts`` directory.


Creating Posts
--------------

You can create posts manually by creating a new file in the ``_posts``
directory. The filename is important (details about its expected format
can be found in the "A Note About Posts" section). However, if you'd
rather ``nanogen`` do this for you, then you can use the ``new``
command. The only required argument to this command is the title of the
post being generated::

    $> nanogen new "Example Post Title"

Running this will create a file in the ``_posts`` directory, with front
matter and placeholder text. By default, this command will supply a
value for ``layout`` in the front-matter of ``article.html``. If you'd
like to use a different layout for your new post, you can use the
``--layout`` (or ``-l``) flag::

    $> nanogen new --layout example.html "Example Post Title"

*Note*: The ".html" in the layout is optional; if it's not provided,
``nanogen`` will add it for you.


Building
--------

Once you're ready to generate your site, you can use the ``build``
command::

    $> nanogen build

This command will walk your directory, process any valid files it
finds, and will write all the generated files into a ``_site`` folder.
Although you will want to preview this on your local development
system (see the following section for how to do this), the ``_site``
folder can be uploaded to your web host as-is, and served as the root
for your web server.

*Note*: before each build ``nanogen`` will run the ``clean`` command.
``clean`` will remove the ``_site`` directory and all of its contents,
so it's not a good idea to add anything to the ``_site`` directory
that you intend to keep between builds.


Previewing Your Site
--------------------

To see what your site will look like *before* you upload it to a live
webserver for the world to see, ``nanogen`` provides a built-in server
that allows you to preview your generated site::

    $> nanogen preview

This command will start a server that listens on ``localhost`` port
``8080``. Simply point a web browser to ``http://localhost:8080`` to
see how your site looks. If you'd like to use a different hostname or
port, ``nanogen`` provides an option for each (``-h|--host, and
-p|--port``, respectively). The following example will start a server
that listens on ``local.dev`` port ``8000`` (http://local.dev:8000)::

    $> nanogen preview --host local.dev --port 8000


Cleaning
--------

If your ``_site`` folder somehow gets corrupted, or you'd simply like
to generate your site from scratch, you can uses ``nanogen``'s
``clean`` command::

    $> nanogen clean

There is no undo or confirmation when running this command.


``nanogen`` Content Types
=========================

Posts
-----

For ``nanogen`` to "publish" (convert from Markdown to HTML) your
posts, two things must be true:

#. they must be located in the ``_posts`` directory, and
#. they must be named like this: ``<year>-<month>-<day>-<name>.<ext>``

    - ``<year>`` is a 4-digit year; ``<day>`` and ``<month>`` are
      two-digits.
    - ``<name>`` is any slugified string that helps you identify the
      file.
    - the ``<ext>`` must be a valid `Markdown`_ extension: ``md``,
      ``mdown``, or ``markdown``.

Examples::

    # valid filename
    2015-11-01-this-charming-man.md

    # invalid filename
    15-11-1-bigmouth-strikes-again.txt

Files in this folder that don't match the above description will be
skipped and will not be part of the generated site. The content of the
post files follows the somewhat-standard format of `YAML`_ front-matter
followed by a separator, followed by a body written in `Markdown`_.
Below is an example of what this format looks like::

    ----
    title: This is an example blog post
    slug: example-post
    layout: post.html
    ----
    
    Everything from this point forward will be process as **Markdown**.
    You can _format_ your text however you please. Please check out the
    Markdown Documentation if you're unfamiliar with Markdown syntax.


The only required field in the front-matter is ``title``. Two optional
fields are ``slug`` and ``layout``. If these aren't present, defaults
will be used. ``slug`` defaults to the ``<name>`` field in the post's
filename, and ``layout`` defaults to ``article.html``. Any other fields
you add to the front-matter will be ignored by ``nanogen``, but are
passed to and can be used by your templates.

Files in ``_posts`` will be "published" into folders based on the date
in their filename, which is assumed to be their publish date. For
example, a blog post with the filename ``2014-11-08-example-post.md``
will be processed into ``_site/<year>/<month>/<name>.html``.

Draft posts aren't an official feature of ``nanogen``, however they are
possible. By default, when ``nanogen`` generates a site it ignores any
directories and files that start with a ``_`` or a ``.``. If you'd like
to maintain drafts of your posts, you can create a ``_drafts`` folder
and ``nanogen`` will ignore it during site generation.


Non-Post Content
----------------

For pages not intended to be blog posts (index pages, a post archive,
about pages, contact pages, etc), ``nanogen`` will simply pick them up
as it processes files and folders. These files do not use the
front-matter/Markdown format, but are instead treated as raw templates.
Their location relative to the root folder will determine their
placement in the published site folder. For example, an ``about.html``
file in the ``blog`` folder will become ``_site/about.html`` in the
generated site.


Static Files
------------

If you have any files that you'd like to include in the published site
(JavaScript files, CSS files, images, etc), but that shouldn't be
processed in any way, you can have ``nanogen`` copy them into the
generated site by using ``keep`` in the site's configuration. See the
Configuration section below for more information.


Configuration
=============

In addition to the per-post configuration (front-matter), there is
also a site-wide level of configuration available to all posts and
templates. This configuration is stored in ``config.yaml`` in the
project root. It isn't strictly required, but ``nanogen`` will warn you
if it doesn't find one. Below is an example of a typical
``config.yaml`` file::

    title: cubicle17
    author: Bill Israel
    url: http://cubicle17.com/
    keep: [img, css, js]

None of the fields in ``config.yaml`` are required, but anything
defined here will be passed to all templates. In the templates,
everything defined in this file will be available under the ``site``
variable. For example, to print the ``url`` variable from the above
example, use ``{{ site.url }}`` in your template.

``keep`` is the only key in the configuration file that ``nanogen``
explicitly looks for. If it's found, ``nanogen`` expects it to be a
list of directories names (relative to the project's root dir) that
need to be copied into the generated site structure. In the above
example, ``img``, ``css``, and ``js`` are all in the project's root
directory.


Templates
=========

``nanogen`` uses `Jinja2`_ for its templating. If you need information
about Jinja's syntax, please `refer to their documentation
<http://jinja.pocoo.org/docs/>`_.

``nanogen`` passes two variables to every template. To single-
post pages it passes the site-wide configuration under a variable
named ``site``, as well as all the post-specific configuration
(front-matter) via a variable named ``post``. To non-post pages,
``nanogen`` passes the site-wide configuration (again under the
``site`` variable), as well as a list of all posts under a variable
named ``posts``.


Misc Notes
==========


#. ``nanogen`` doesn't (and likely won't) provide a ``watch`` mechanism
   found in other static site generators. If you'd like this
   functionality, you can use a tool like `Watchman`_ or simply run
   ``build`` in an infinite loop. The following example will run a
   build every second::

    $> while [ 1 ]; do nanogen build; sleep 1; done

   If you run this in one tab, and preview in another, trust me it's
   just like having a ``watch`` command.


License
#######

``nanogen`` is MIT licensed. Please see included ``LICENSE`` file for
more information.


Author
######

`Bill Israel`_ - `bill.israel@gmail.com`_


.. _Markdown: http://daringfireball.net/projects/markdown
.. _YAML: http://yaml.org/
.. _Jinja2: http://jinja2.pocoo.org/
.. _Watchman: https://facebook.github.io/watchman/
.. _Bill Israel: http://billisrael.info/
.. _bill.israel@gmail.com: mailto:bill.israel@gmail.com


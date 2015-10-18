# nanogen

A very small static site generator written in Python.

![Latest PyPI version](https://img.shields.io/pypi/v/nanogen.svg)

## Installation

The best way to install `nanogen` is through `pip`:

    $> pip install nanogen

If you don't want to install it via `pip`, you can install it by hand:

    $> git clone https://github.com/epochblue/nanogen
    $> cd nanogen
    $> python setup.py install

**Note**: To avoid possible dependency version issues, I advise installing
`nanogen` into a virtual environment, rather than installing it globally.


## How To Use

### Initializing

Once `nanogen` is installed, navigate to the directory you'd like to use as your
new blog. Our examples will use a `blog` directory in our home directory:

    $> mkdir blog
    $> cd blog

Once there, run `nanogen`'s `init` command to get started:

    $> nanogen init

Running this command will generate the basic directories used by `nanogen` to
build your static site. When this command completes, your `blog` directory will
look like this:

    ~/blog
    |-- _posts
    `-- _layouts

These are all the only two folders required by `nanogen`, and cannot currently
be changed by the user. If you're creating a blog-style site, your individual
posts will go in the `_posts` directory, and your site's templates will go in
the `_layouts` directory.


### Publishing Posts

For `nanogen` to "publish" your posts, two things must be true:

1. they must be located in the `_posts` directory, and
2. they must be named like this: `<year>-<month>-<day>-<name>.<ext>`

    * `<year>` is a 4-digit year; `<day>` and `<month>` are two-digits
    * the `<ext>` must be a valid [Markdown][] extension: `md`, `mdown`, `markdown`

Files in this folder that don't match the above pattern will be skipped and
will not be part of the generated site. The content of the post files follows
the somewhat-standard format of [YAML][] front-matter followed by a
[Markdown][] body. Below is an example of what this format looks like:

    ----
    title: This is an example blog post
    slug: example-post
    layout: post.html
    ----

    Everything from this point forward will be process as **Markdown**.
    You can _format_ your text however you please. Please check out the Markdown
    Documentation if you're unfamiliar with Markdown syntax.

The only required field in the front-matter is `title`. Two optional fields are
`slug` and `layout`. If these aren't present, defaults will be used. `slug`
defaults to the `<name>` field in the post's filename, and `layout` defaults to
`article.html`. Any other fields you add to the front-matter will be ignored by
`nanogen`, but are passed to and can be used by your templates.

Files in `_posts` will be "published" into folders based on the date in their
filename, which is assumed to be their publish date. For example, a blog post
with the filename `2014-11-08-example-post.html` will be processed into a
date-specific folder: `site/<year>/<month>/<name>.html`.

Draft posts aren't an official feature of `nanogen`, however they are possible.
By default, when `nanogen` generates a site it ignores any directories that
start with a `_`. If you'd like to maintain drafts of your posts, you can
create a `_drafts` folder and `nanogen` will dutifully ignore it during site
generation.


### Publishing Non-Post Content

For pages that aren't intended to be blog posts (An index page, a post archive,
About pages, Contact pages, etc), `nanogen` will simply pick them up as it
processes files and folders. These files don't use the front-matter/Markdown
format, but are instead treated as raw templates. Their location relative to the
root folder will determine their placement in the published site folder.


### Static Files

If you have any files that you'd like to include in the published site you can
use the `keep` field in the site configuration. Common uses for this would be
CSS or JavaScript files that you need to help render the final site. See the
[Configuration](#configuration) section for more information.


### Building

Once you're ready to generate your site, you can use the `build` command:

    $> nanogen build

This command will walk your directory, process any valid files it finds, and
will write all the generated files into a `_site` folder. Although you will want
to check this on your local development system, the `site` folder can be
uploaded to your web host as-is and served as the root for your web server.

_Note_: before each build `nanogen` will reset the `_site` directory, so it's
not a good idea to add anything to the `_site` directory that you intend to
keep between builds.


### Cleaning

`nanogen` provides a `clean` command to remove your `site` folder if it somehow
gets corrupted or you would like to generate your site from scratch:

    $> nanogen clean


### Configuration

In addition to the per-post configuration (front-matter), there is also a
site-wide level of configuration available to all posts and templates. This
configuration is stored in `config.yaml` in the project root. It isn't strictly
required, but `nanogen` will warn you if it doesn't find one. Below is an
example of a typical `config.yaml` file:

```yaml
title: cubicle17
author: Bill Israel
url: http://cubicle17.com/
keep: [static, css, js]
```

None of the fields in `config.yaml` are required, but anything defined will be
passed to all templates. In the templates, anything defined in this file will be
available under a special variable called `site`. For example, to use the `url`
variable from the above example, use`{{ site.url }}` in your template.

`keep` is the only key in the configuration file that `nanogen` explicitly looks
for. If it's found, `nanogen` expects it to be a [YAML][] list of directories
(relative to the project's root dir) that need to be copied into the generated
site structure.


## Templates

`nanogen` uses [Jinja2][] for its templating. If you need information about how
Jinja templates work, please [refer to their documentation][jinja-docs].

`nanogen` passes a few things to each template, however. To single-post pages
it passes the site-wide configuration under a variable called `site`, as well
as all the information about the single post via a variable called `post`. To
all other templates `nanogen` again passes the site-wide configuration under the
`site` variable, as well as a list of all posts under a variable called `posts`.


## Misc Notes

1. `nanogen` doesn't provide a `watch` mechanism found in other static site
generators. If you'd like this functionality, you can use a tool like
[Watchman][] or simply run `build` in an infinite loop. The following example
will run a build every second:

        $> while [ 1 ]; do nanogen build; sleep 1; done


## License

`nanogen` is MIT licensed. Please see included `LICENSE` file for more information.


## Author

[Bill Israel](http://billisrael.info/) - [bill.israel@gmail.com](mailto:bill.israel@gmail.com)


[markdown]: http://daringfireball.net/projects/markdown/
[yaml]: http://www.yaml.org
[watchman]: https://github.com/facebook/watchman
[jinja2]: http://jinja.pocoo.org/
[jinja-docs]: http://jinja.pocoo.org/docs/dev/

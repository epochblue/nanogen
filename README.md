# nanogen

A very small static site generator written in Python.

## Installation

The best way to install `nanogen` is through `pip`:

    $> pip install nanogen

If you don't want to install it via `pip`, you can install it by hand:

    $> git clone https://github.com/epochblue/nanogen
    $> cd nanogen
    $> python setup.py install

**Note**: To avoid possible dependency version issues, we advise installing
`nanogen` into a virtual environment, rather than installing it globally.


## How To Use

### Initializing

Once `nanogen` is installed, navigate to the directory you'd like to use as your
new blog. Our examples will use a `blog` directory in our home directory:

    cd ~/blog

Once you're there, you can run `nanogen`'s `init` command to get started:

    nanogen init

Running this command will generate the base directories and files that are
used by `nanogen` to build your static site. When this command completes,
our blog directory should look like this:

    ~/blog
    |-- _pages
    |-- _posts
    |-- _drafts
    |-- _static
    |-- _templates
    |   |-- archive.html
    |   |-- article.html
    |   |-- base.html
    |   |-- index.html
    |   `-- rss.xml
    `-- config.yaml

These are all the default files and folders used by `nanogen`. The folder names
and the templates for collection views (`archive.html`, `index.html`, and
`rss.xml`) are currently not editable by the user. By default, `nanogen` will use
`article.html` as the template for articles and pages, but this is overrideable
in the front-matter for each page and article.

Blog posts should be placed in the `_posts` folder, and named like this:

    <publish_year>-<publish_month>-<publish_day>-<name>.md

Files in this folder that don't match the above pattern will be skipped and
will not be part of the build. Below is an example post:

    ----
    title: This is an example blog post
    slug: example-post
    template: article2.html
    ----

    Everything from this point forward will be process as **Markdown**.
    You can _format_ your text according however you please. Please check out
    the Markdown Documentation if you're unfamiliar with Markdown synxtax.

The `title` and `slug` are required fields in the front-matter. `template` is
optional, but is required if you'd like the post to be rendered using a
template other than the default `article.html`. Blog post entries will be placed
into folders based on their publish date. For example, a blog post with the
filename `2014-11-08-example-post.html` will be processed into a date-specific
folder: `site/<year>/<month>/<day>-<name>.html`.

Draft posts can be stored in the `_drafts` folder. This folder is included for
convenience, and is never read/scanned/processed by `nanogen`.

For pages that aren't intended to be blog posts (About pages, Contact pages,
etc), the `_pages` folder should be used. Files in this folder don't have a
specific naming convention they expect. Whatever the file is named in this
folder will be the same as its name in the build folder. All pages files will
be processed into the top-level `site` directory.

Static files (CSS, JavaScript, images) should be placed in the `_static` folder.
Upon building, these files will be copied into a top-level `static` folder
whose structure matches exactly what it finds in `_static`.


### Building

Once your files are all in the right places and you're ready to generate your
site, you can use the `build` command:

    nanogen build

This command will walk your `_posts` and `_pages` folders, process any valid
files it finds, and will write all the generated files into a `site` folder.
Although you will want to check this on your local development system, the
`site` folder should be ready to upload to your web host and served up as the
root for you web server.


### Cleaning

`nanogen` provides a `clean` command to remove your `site` folder if it somehow
get scorrupted or you would like to generate your site from scratch:

    nanogen clean


## Misc Notes

1. `nanogen` doesn't provide a `watch` mechanism found in other static site
generators. If you'd like this functionality, you can simply run `build` in
an infinite loop in Bash. The following example will run a build every second:

        $> while :; do nanogen build; sleep 1; done

2. The items in the front-matter in the above example are the minimal required
by `nanogen`. However, you can include any custom fields you'd like to include.
All key/value pairs in the front-matter are passed to each template, so you can
use these custom front-matter fields in your templates if you'd like to.


## License

`nanogen` is MIT licensed. Please see included `LICENSE` file for more information.


## Author

[Bill Israel](http://billisrael.info/) - [bill.israel@gmail.com](mailto:bill.israel@gmail.com)


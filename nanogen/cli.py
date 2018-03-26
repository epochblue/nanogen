import datetime
import os

import click

from nanogen import logger
from nanogen import version
from nanogen import models


@click.group()
@click.option('-v', '--verbose', count=True, help='Turn on verbose output.')
@click.version_option(version=version.version)
def cli(verbose):
    logger.init_logger(verbose)


@cli.command()
def init():
    """Initialize the current directory."""
    blog = models.Blog(os.getcwd())
    blog.init()


@cli.command()
def clean():
    """Clean any generated files."""
    blog = models.Blog(os.getcwd())
    blog.clean()


@cli.command()
def build():
    """Start a build of the site."""
    blog = models.Blog(os.getcwd())
    blog.build()


@cli.command()
@click.argument('title')
def new(title):
    """Create a new post with the given title"""
    blog = models.Blog(os.getcwd())
    try:
        blog.new_post(title)
    except ValueError as ve:
        click.ClickException(str(ve))

@cli.command()
@click.argument('title')
def draft(title):
    """Create a new draft post with the given title"""
    blog = models.Blog(os.getcwd())
    try:
        blog.new_post(title, draft=True)
    except ValueError as ve:
        click.ClickException(str(ve))


@cli.command()
@click.option('-h', '--host', default='localhost', help='The hostname to serve on')
@click.option('-p', '--port', default=8080, type=int, help='The port to serve on')
def preview(host, port):
    """Serve a preview of the site on HOST and PORT."""
    blog = models.Blog(os.getcwd(), is_preview=True)
    blog.clean()
    blog.build()

    try:
        import SimpleHTTPServer, BaseHTTPServer
        handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        handler.protocol_version = 'HTTP/1.0'
        httpd = BaseHTTPServer.HTTPServer((host, port), handler)
    except ImportError:
        import http.server
        handler = http.server.SimpleHTTPRequestHandler
        handler.protocol_version = 'HTTP/1.0'
        httpd = http.server.HTTPServer((host, port), handler)

    try:
        click.secho('Serving your site on http://{host}:{port}/...'.format(host=host, port=port))
        click.secho('Press <Ctrl-C> to stop the server.\n')

        os.chdir(blog.PATHS['preview'])

        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


@cli.command()
@click.argument('filename')
def publish(filename):
    """Move a post from the _drafts dir to the _posts dir."""
    blog = models.Blog(os.getcwd())

    try:
        blog.publish(filename)
    except ValueError as ve:
        click.ClickException(str(ve))

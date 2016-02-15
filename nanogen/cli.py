import os

import click

import logger
import nanogen
from . import __version__


@click.group()
@click.option('-v', '--verbose', count=True, help='Turn on verbose output.')
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, verbose):
    logger.init_logger(verbose)


@cli.command()
@click.pass_context
def init(ctx):
    """Initialize the current directory."""
    nanogen.init()


@cli.command()
@click.pass_context
def clean(ctx):
    """Clean any generated files."""
    nanogen.clean()


@cli.command()
@click.pass_context
def build(ctx):
    """Start a build of the site."""
    nanogen.clean()
    nanogen.build()


@cli.command()
@click.argument('title')
@click.option('-l', '--layout', default='article.html', help='The layout template the post will use')
@click.pass_context
def new(ctx, title, layout):
    """Create a new post with the given title"""
    try:
        nanogen.new(title, layout)
    except ValueError as ve:
        click.ClickException(ve.message)


@cli.command()
@click.option('-h', '--host', default='localhost', help='The hostname to serve on')
@click.option('-p', '--port', default=8080, type=int, help='The port to serve on')
@click.pass_context
def preview(ctx, host, port):
    """Serve a preview of the site on HOST and PORT."""
    site_dir = nanogen.get_site_dir()
    if not os.path.isdir(site_dir):
        click.ClickException('Unable to locate _site directory. Did you forget to run `nanogen build`?')

    try:
        import SimpleHTTPServer, BaseHTTPServer
        handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        handler.protocol_version = 'HTTP/1.0'
        httpd = BaseHTTPServer.HTTPServer((host, 8080), handler)
    except ImportError:
        import http.server
        handler = http.server.SimpleHTTPRequestHandler
        handler.protocol_version = 'HTTP/1.0'
        httpd = http.server.HTTPServer(host, 8080, handler)

    try:
        click.secho('Serving your site on http://{host}:{port}/...'.format(host=host, port=port))
        click.secho('Press <Ctrl-C> to stop the server.\n')
        os.chdir(site_dir)
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()

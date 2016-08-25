import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter


class NanogenRenderer(mistune.Renderer):
    def block_code(self, code, lang=None):
        if lang is None:
            return '\n<pre><code>%s</code></pre>\n' % mistune.escape(code)
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter()
        return highlight(code, lexer, formatter)

markdown = mistune.Markdown(renderer=NanogenRenderer())

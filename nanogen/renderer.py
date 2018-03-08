import mistune
from mistune_contrib import highlight


class NanogenRenderer(highlight.HighlightMixin, mistune.Renderer):
    pass

markdown = mistune.Markdown(renderer=NanogenRenderer(inlinestyles=False, linenos=False))

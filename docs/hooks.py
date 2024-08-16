def on_page_markdown(markdown, **kwargs):
    return markdown.replace("<BLANKLINE>", "")

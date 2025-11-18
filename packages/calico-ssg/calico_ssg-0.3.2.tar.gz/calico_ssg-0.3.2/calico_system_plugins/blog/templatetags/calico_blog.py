from django import template
from django.utils.text import capfirst, slugify

from calico.exceptions import PageDoesNotExist
from calico.utils import calico_setting

from ..utils import get_author


register = template.Library()


@register.filter
def author_details(author_slug):
    try:
        post = get_author(author_slug)
    except PageDoesNotExist:
        return {
            'name': capfirst(author_slug),
            'title': capfirst(author_slug),
        }

    rv = post.metadata
    if 'name' not in rv:
        rv['name'] = rv.get('title', capfirst(author_slug))
    rv['content'] = post.md_content
    return rv


@register.filter
def author_link(author_slug):
    return f'/{calico_setting("BLOG_AUTHOR_DIR")}/{author_slug}.html'


@register.filter
def authored(author_slug):
    from calico.models import Site

    slug = slugify(author_slug) if author_slug else author_slug

    return [post.meta.data for post in Site().get_posts(slug)]


@register.filter
def tag_link(tag):
    return f'/{calico_setting("TAGS_PAGE")}.html?tag={slugify(tag)}'


@register.filter
def latest_posts(count=5):
    return authored(None)[:count]

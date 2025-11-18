from datetime import datetime

import markdown2
from django.contrib.syndication.views import Feed
from django.http import Http404
from django.utils.text import Truncator, capfirst, slugify

from calico.exceptions import PageDoesNotExist
from calico.utils import calico_setting, get_tags

from .utils import blog_posts_per_author, get_author


class GeneralFeed(Feed):
    _link = f'{calico_setting("FEEDS_BASE")}{calico_setting("MAIN_FEED")}'

    def title(self):
        from calico.models import Site

        return Site().metadata.get('title')

    def description(self):
        from calico.models import Site

        return Site().metadata.get('main_feed_description')

    def _abs_prefix(self):
        scheme = self.request.scheme
        if calico_setting('FORCE_HTTPS'):
            scheme = 'https'
        elif calico_setting('FORCE_HTTP'):
            scheme = 'http'

        host = calico_setting('HOST')
        if host == 'localhost':
            host = self.request.get_host()

        return f'{scheme}://{host}'

    def link(self):
        return self._abs_prefix()

    def get_feed(self, obj, request):
        self.request = request
        return super().get_feed(obj, request)

    def items(self):
        return blog_posts_per_author(None)

    def item_title(self, item):
        return item.metadata.get('title', capfirst(item.slug.rsplit('/', 1)[-1]))

    def item_description(self, item):
        rv = ''
        if calico_setting('RSS_CONTENT') != 'full':
            if 'description' in item.metadata:
                rv = item.metadata['description']
            elif 'excerpt' in item.metadata:
                rv = item.metadata['excerpt']
        if rv == '':
            rv = item.md_content

        rv = markdown2.markdown(rv)

        if truncate_word := calico_setting('RSS_WORDS'):
            rv = Truncator(rv).words(truncate_word, html=True, truncate=' …')

        return rv

    # item_link is only needed if NewsItem has no get_absolute_url method.
    def item_link(self, item):
        return f'{self._abs_prefix()}{item.url}'

    def item_author_name(self, item):
        if 'author' not in item.metadata:
            return None

        author_slug = item.metadata['author']
        try:
            post = get_author(author_slug)
        except PageDoesNotExist:
            return capfirst(author_slug)

        rv = post.metadata
        if 'name' not in rv:
            return rv.get('title', capfirst(author_slug))

        return rv['name']

    def item_author_email(self, item):
        if 'author' not in item.metadata:
            return None

        author_slug = item.metadata['author']
        try:
            post = get_author(author_slug)
        except PageDoesNotExist:
            return None

        return post.metadata.get('email', None)

    def item_author_link(self, item):
        if 'author' not in item.metadata:
            return None

        author_slug = item.metadata['author']
        try:
            post = get_author(author_slug)
        except PageDoesNotExist:
            return None

        return f'{self._abs_prefix()}{post.url}'

    def item_pubdate(self, item):
        if not isinstance(item.published_at, datetime):
            return datetime.combine(item.published_at, datetime.min.time())
        return item.published_at

    def item_updateddate(self, item):
        return item.lastmod

    def item_categories(self, item):
        return item.metadata.get('tags', None)

    def categories(self):
        rv = [k[0] for k in get_tags(None)]
        return rv


class TagFeed(GeneralFeed):
    def title(self, obj):
        from calico.models import Site

        return Site().metadata.get('tag_feed_title', '').format(obj=obj)

    def link(self, obj):
        return calico_setting('TAG_FEED_URL', '').format(tag=slugify(obj))

    def description(self, obj):
        from calico.models import Site

        return Site().metadata.get('tag_feed_descript', '{obj}').format(obj=capfirst(obj))

    def get_object(self, request, tag):
        posts = get_tags(None)
        tags = {slugify(t[0]): t[0] for t in posts}
        if tag not in tags:
            raise Http404

        rv = tags[tag]
        self.posts = dict(posts)[rv]
        return rv

    def items(self, obj):
        return self.posts

    def categories(self, obj):
        tags = []
        for post in self.posts:
            tags.extend(post.metadata.get('tags', []))
        return set(tags)

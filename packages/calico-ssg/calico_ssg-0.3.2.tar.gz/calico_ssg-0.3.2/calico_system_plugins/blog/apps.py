from django.apps import AppConfig
from django.utils.text import slugify

from calico import hook


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calico_system_plugins.blog'

    def ready(self):
        from calico import models

        def _filter_posts_per_author(self, posts, author_slug):
            return [p for p in posts if author_slug == slugify(p.meta.get('author', ''))]

        models.Site._filter_posts_per_author = _filter_posts_per_author

        def get_posts(self, author_slug=None, tag=None):
            posts = self._posts

            if tag:
                posts = self._tags[tag]

            if author_slug:
                posts = self._filter_posts_per_author(posts, author_slug)

            return sorted(posts, key=lambda p: str(p.meta.get('published_date')), reverse=True)

        models.Site.get_posts = get_posts


@hook
def installed_apps():
    return ['calico_system_plugins.blog']


@hook
def auto_load_tags():
    return ['calico_system_plugins.blog.templatetags.calico_blog']


@hook
def calico_defaults():
    return {
        'BLOG_AUTHOR_DIR': 'blog/author',
        'BLOG_DIR': 'blog',
        'FEEDS_BASE': 'blog/feeds/',
        'MAIN_FEED': '_rss.xml',
        'RSS_CONTENT': 'partial',
        'RSS_WORDS': 80,
        'TAG_FEED_URL': 'blog/feed/{tag}.xml',
    }


@hook
def urlpatterns():
    from django.utils.text import slugify
    from django_distill import distill_path

    from calico.utils import calico_setting, get_tags

    from .feeds import GeneralFeed, TagFeed

    urlpatterns = []
    feeds_base = calico_setting('FEEDS_BASE')
    main_feed = calico_setting('MAIN_FEED')

    if feeds_base:
        if main_feed:
            urlpatterns += [
                distill_path(
                    f'{feeds_base}/{main_feed}',
                    GeneralFeed(),
                    name='general_feed',
                    distill_func=lambda: None,
                    distill_file=f'{calico_setting("FEEDS_BASE")}/_rss.xml',
                ),
            ]

        tags = get_tags(None)
        if len(tags):
            urlpatterns += [
                distill_path(
                    calico_setting('TAG_FEED_URL', '').format(tag='<slug:tag>'),
                    TagFeed(),
                    name='tag_feed',
                    distill_func=lambda: [slugify(t[0]) for t in tags],
                ),
            ]
    return urlpatterns


def page_is_post(site, page):
    if page.is_hidden:
        return None

    if page.meta.get('widget', '') in ('blog_post', 'blog.post'):
        page.meta.data['published_date'] = page.published_at
        page.meta.data['url'] = page.url
        page.meta.data['content'] = page.md_content
        page.meta.data['readtime'] = page.readtime

        return page


@hook
def site_groupings():
    return [('posts', list, page_is_post, 'append')]

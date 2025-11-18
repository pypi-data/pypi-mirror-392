import os

from django.utils.text import slugify

from calico.utils import calico_setting


def get_author(author_slug):
    from calico.models import Page

    return Page(os.path.join(calico_setting('BLOG_AUTHOR_DIR'), author_slug))


def blog_posts_per_author(author_slug):
    from calico.models import Page

    subdir = calico_setting('BLOG_DIR')
    posts = []

    slug = slugify(author_slug) if author_slug else None

    for post in Page.pages_in_dir(subdir=subdir):
        if post.metadata.get('widget', '') not in ('blog_post', 'blog.post'):
            continue
        if slug and slug != slugify(post.metadata.get('author', '')):
            continue
        post.metadata['published_date'] = post.published_at
        post.metadata['url'] = post.url
        posts.append(post)
    return sorted(posts, key=lambda x: str(x.metadata['published_date']), reverse=True)

from django import template

from calico.models import Site


register = template.Library()


@register.filter
def collection_top(item, collection=None):
    return Site().get_collection(
        collection or item.metadata['collection'],
        sort_by=item.metadata.get('collection_sort_by', 'slug'),
        count=int(item.metadata.get('top_count', 0)),
    )


@register.filter
def collection_grouped_top(item):
    return Site().get_collection(
        item.metadata['collection'],
        sort_by=item.metadata.get('collection_sort_by', 'slug'),
        group_by=item.metadata['group_by'],
        count=int(item.metadata.get('top_count', 0)),
    )

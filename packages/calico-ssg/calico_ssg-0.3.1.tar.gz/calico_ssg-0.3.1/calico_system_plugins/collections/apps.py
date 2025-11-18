from collections import defaultdict

from django.apps import AppConfig

from calico import hook


class CollectionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calico_system_plugins.collections'

    def ready(self):
        from calico import models

        def get_collection(self, collection, sort_by='slug', count=0, group_by=None):

            print(collection, len(self._collections.keys()), self._collections[collection])

            if sort_by[0] == '-':
                rev = True
                sort_by = sort_by[1:]
            else:
                rev = False

            rv = sorted(
                self._collections[collection],
                key=lambda x: str(x.meta.get(sort_by)),
                reverse=rev
            )

            if count:
                rv = list(rv)[:count]

            if group_by:
                grouped = defaultdict(list)

                for item in rv:
                    grouped[item.meta.get(group_by)].append(item)

                return grouped.items()

            return rv

        models.Site.get_collection = get_collection


@hook
def installed_apps():
    return ['calico_system_plugins.collections']


def page_is_collection(site, page):

    if not page.is_hidden:
        return

    if collections := page.meta.get('member_of'):
        if isinstance(collections, str):
            site._collections[collections].append(page)
        else:
            for collection in collections:
                site._collections[collection].append(page)


@hook
def site_groupings():
    return [('collections', lambda: defaultdict(list), page_is_collection, 'no_op')]


@hook
def auto_load_tags():
    return ['calico_system_plugins.collections.templatetags.calico_collections']

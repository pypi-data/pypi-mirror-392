## Very much inspired by https://github.com/simonw/djp/issues/17#issuecomment-2378164823
from collections import defaultdict
import importlib
import itertools
from pathlib import Path

from django.utils.text import slugify
from pluggy import HookimplMarker

from djp import pm


hook = HookimplMarker('djp')

c_hookspec_module = importlib.import_module('calico.hookspecs')
pm.add_hookspecs(c_hookspec_module)


def find_plugins_in_dir(plugins_dir, prefix):
    return {
        f"{prefix}.{plugin_entrypoint.parent.name}": plugin_entrypoint.parent
        for plugin_entrypoint in sorted(plugins_dir.glob("*/apps.py"))  # key=get_plugin_order  # see note below
    }


def get_pip_installed_plugins(group='djp'):
    """replaces pm.load_setuptools_entrypoints("djp")"""
    import importlib.metadata

    detected_plugins = {}   # module_name: module_dir_path
    for dist in list(importlib.metadata.distributions()):
        for entrypoint in dist.entry_points:
            if entrypoint.group != group or pm.is_blocked(entrypoint.name):
                continue
            detected_plugins[entrypoint.name] = Path(entrypoint.load().__file__).parent
            # pm.register(plugin, name=ep.name)
            # ^ dont do this now, we wait till load_plugins() is called
    return detected_plugins


def get_plugins_in_dirs(plugin_dirs):
    detected_plugins = {}
    for plugin_prefix, plugin_dir in plugin_dirs.items():
        detected_plugins.update(find_plugins_in_dir(plugin_dir, prefix=plugin_prefix))
    return detected_plugins


def load_plugins(plugins_dict, exclude_plugins=[]):
    loaded_plugins = {}
    for plugin_module, plugin_dir in plugins_dict.items():
        if plugin_module in exclude_plugins:
            print(f'🚫 Ignoring plugin: {plugin_module}')
            continue
        # print(f'Loading plugin: {plugin_module} from {plugin_dir}')
        plugin_module_loaded = importlib.import_module(plugin_module + '.apps')
        pm.register(plugin_module_loaded)  # assumes hookimpls are imported in plugin/apps.py
        loaded_plugins[plugin_module] = plugin_module
        print(f'🧩 Loaded plugin: {plugin_module}')
    return loaded_plugins


def auto_load_tags():
    return list(itertools.chain(*pm.hook.auto_load_tags()))


class FileListAlteration:
    def __init__(self, new_urls):
        if isinstance(new_urls, str):
            self.new_urls = [new_urls]
        else:
            self.new_urls = new_urls


class ReplaceFile(FileListAlteration):
    def __init__(self, to_replace, new_urls):
        self.to_replace = to_replace
        super().__init__(new_urls)


class Overwrite(FileListAlteration):
    pass


def _make_static(value):
    from calico.utils import static_or_not

    if isinstance(value, str):
        value = [value]

    return [
        static_or_not(v)
        for v in value
    ]


def _one_file(value, files, to_replace, static=False):
    _stat = _make_static if static else lambda x: [x] if isinstance(x, str) else x
    if isinstance(value, FileListAlteration):
        # only possible alteration so far is ReplaceFile
        assert value.to_replace not in to_replace, \
            f'Replace conflict detected bewteen {value.to_replace}: {value.new_urls}' + \
            f' and {to_replace[value.to_replace]}'
        to_replace[value.to_replace] = _stat(value.new_urls)

        return

    name = None

    if isinstance(value, tuple):
        name, value = value
    if name is None:
        name = slugify(value.rsplit('/', 1)[-1])

    files[name].extend(_stat(value))


def _files(files_lists, raw=False, static=True):
    to_replace = {}
    files = defaultdict(list)

    for returned in files_lists:
        if any(isinstance(returned, t) for t in (str, FileListAlteration)):
            _one_file(returned, files, to_replace, static=static)
        else:
            # Assuming iterable
            for item in returned:
                _one_file(item, files, to_replace, static=static)

    files.update(to_replace)

    if raw:
        return files

    return list(itertools.chain(*files.values()))


def available_themes(raw=False):
    return _files(pm.hook.declare_theme(), raw=raw, static=False)


def calico_media(media_type, theme, raw=False, extra=None):
    hook = getattr(pm.hook, f'calico_{media_type}')
    if isinstance(extra, Overwrite):
        lst = [extra]
    else:
        lst = hook(theme=theme)
        if extra is not None:
            lst += extra

    return _files(lst, raw=raw)


def default_calico_settings():
    settings = {}
    for setting in pm.hook.calico_defaults():
        settings.update(setting)
    return settings


def get_list_from_hook(hook):
    return list(set(itertools.chain(*getattr(pm.hook, hook)())))

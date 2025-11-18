import djp


@djp.hookimpl
def installed_apps():
    return ['picocss']

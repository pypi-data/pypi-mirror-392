from beetle.translate import _
from beetle import _state
from beetle._state import LOADED_PROFILES
from beetle_runtime.project import PROJECTINFO
from beetle_runtime import BeetleError, _source
from beetle_runtime._beetle import get_core_settings, get_default_profiles
from beetle_runtime._settings import load_settings, expand_placeholders
from beetle_runtime._source import get_settings_paths
from os.path import abspath

import sys

"""
beetle populates SETTINGS with the current build settings. A typical example is
SETTINGS['app_name'], which you define in src/build/settings/base.json.
"""
SETTINGS = _state.SETTINGS

IGNORE_BEETLEERROR = ['-h', 'template_list', 'update_template', 'add_template', 'delete_template', 'startproject']


def init(project_dir):
    """
    Call this if you are invoking neither `beetle` on the command line nor
    beetle.cmdline.main() from Python.
    """
    if sys.version_info[0] != 3 or sys.version_info[1] < 6:
        raise BeetleError(_(
            'This version of beetle only supports Python >= 3.6'
        ))
    try:
        PROJECTINFO.init_project_info(project_dir)
    except BeetleError as e:
        flag = True
        for cmd in IGNORE_BEETLEERROR:
            if cmd in sys.argv:
                flag = False
        if flag:
            print(e)
    SETTINGS.update(get_core_settings(abspath(project_dir)))
    for profile in get_default_profiles():
        activate_profile(profile)


init.__doc__ = _(
    """
    Call this if you are invoking neither `beetle` on the command line nor
    beetle.cmdline.main() from Python.
    """
)


def activate_profile(profile_name):
    """
    By default, beetle only loads some settings. For instance,
    src/build/settings/base.json and .../`os`.json where `os` is one of "mac",
    "linux" or "windows". This function lets you load other settings on the fly.
    A common example would be during a release, where release.json contains the
    production server URL instead of a staging server.
    """
    LOADED_PROFILES.append(profile_name)
    project_dir = SETTINGS['project_dir']
    try:
        json_paths = get_settings_paths(project_dir, LOADED_PROFILES)
    except BeetleError as e:
        json_paths = []
    core_settings = get_core_settings(project_dir)
    SETTINGS.update(load_settings(json_paths, core_settings))


activate_profile.__doc__ = _(
    """
    By default, beetle only loads some settings. For instance,
    src/build/settings/base.json and .../`os`.json where `os` is one of "mac",
    "linux" or "windows". This function lets you load other settings on the fly.
    A common example would be during a release, where release.json contains the
    production server URL instead of a staging server.
    """
)


def path(path_str):
    """
    Return the absolute path of the given file in the project directory. For
    instance: path('src/main/python'). The `path_str` argument should always use
    forward slashes `/`, even on Windows. You can use placeholders to refer to
    settings. For example: path('${freeze_dir}/foo').
    """
    path_str = expand_placeholders(path_str, SETTINGS)
    try:
        project_dir = SETTINGS['project_dir']
    except KeyError:
        error_message = _("Cannot call path(...) until beetle.init(...) has been "
                          "called.")
        raise BeetleError(error_message) from None
    return _source.path(project_dir, path_str)


path.__doc__ = _(
    """
    Return the absolute path of the given file in the project directory. For
    instance: path('src/main/python'). The `path_str` argument should always use
    forward slashes `/`, even on Windows. You can use placeholders to refer to
    settings. For example: path('${freeze_dir}/foo').
    """
)

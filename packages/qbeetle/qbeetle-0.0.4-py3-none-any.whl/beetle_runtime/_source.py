"""
This module contains functions that should only be called by module `beetle`, or
when running from source.
"""

from beetle_runtime import BeetleError
from beetle_runtime._beetle import get_default_profiles, get_core_settings, \
    filter_public_settings
from beetle_runtime._settings import load_settings
from beetle_runtime.project import PROJECTINFO
from os.path import join, normpath, dirname, pardir, exists
from pathlib import Path

import os


def get_project_dir():
    result = Path(os.getcwd())
    while result != result.parent:
        if (result / 'project.json').is_file():
            return str(result)
        result = result.parent
    raise BeetleError(
        'Could not determine the project base directory. '
        'Was expecting project.json.'
    )


def get_resource_dirs(project_dir):
    PROJECTINFO.init_project_info(project_dir)
    result = [path(project_dir, PROJECTINFO.icons_dir)]
    resources = path(project_dir, PROJECTINFO.medias_dir)
    result.extend(
        join(resources, profile)
        # Resource dirs are listed most-specific first whereas profiles are
        # listed most-specific last. We therefore need to reverse the order:
        for profile in reversed(get_default_profiles())
    )
    return result


def load_build_settings(project_dir):
    PROJECTINFO.init_project_info(project_dir)
    core_settings = get_core_settings(project_dir)
    profiles = get_default_profiles()
    json_paths = get_settings_paths(project_dir, profiles)
    all_settings = load_settings(json_paths, core_settings)
    return filter_public_settings(all_settings)


def get_settings_paths(project_dir, profiles):
    return list(filter(exists, (
        path_fn('%s/%s.json' % (PROJECTINFO.settings_dir, profile))
        for path_fn in (default_path, lambda p: path(project_dir, p))
        for profile in profiles
    )))


def default_path(path_str):
    defaults_dir = join(dirname(__file__), pardir, 'beetle', '_defaults')
    return path(defaults_dir, path_str)


def path(base_dir, path_str):
    return normpath(join(base_dir, *path_str.split('/')))

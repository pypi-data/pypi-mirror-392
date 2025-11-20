from beetle import path, SETTINGS
from beetle._state import LOADED_PROFILES
from beetle.resources import _copy
from beetle_runtime import BeetleError
from beetle_runtime.project import PROJECTINFO
from beetle_runtime._beetle import filter_public_settings
from beetle_runtime._source import default_path
from beetle_runtime.platform import is_mac, is_windows, is_linux
import shutil
import os
import sys
from os import rename, makedirs
from os.path import join, dirname
from pathlib import PurePath
from subprocess import run
from enum import Enum
import pkgutil

import beetle_runtime._frozen


class FreezeTool(Enum):
    pyinstaller = "pyinstaller"
    nuitka = "nuitka"


def run_nuitka(extra_args=None, debug=False):
    if extra_args is None:
        extra_args = []
    app_name = SETTINGS['app_name']
    author = SETTINGS['author']
    version = SETTINGS['version']
    enable_plugin = PROJECTINFO.qt_bindings.lower()
    # Would like log level WARN when not debugging. This works fine for
    # PyInstaller 3.3. However, for 3.4, it gives confusing warnings
    # "hidden import not found". So use ERROR instead.
    log_level = 'DEBUG' if debug else 'ERROR'
    if is_windows():
        nuitka = "nuitka.bat"
    else:
        nuitka = "nuitka"
    args = [
        nuitka,
        "--standalone",
        f"--output-dir={path('target')}",
        f"--output-filename={app_name}",
        f"--enable-plugin={enable_plugin}",
        f"--company-name={author}",
        f"--product-name={author}",
        f"--file-version={version}.0",
        f"--product-version={version}.0",
    ]
    if debug:
        args.extend(["--show-progress", "--show-memory", "--debug"])
    if SETTINGS['nuitka_paramas']['include_package']:
        args.extend(["--include-package=" + ','.join(SETTINGS['nuitka_paramas']['include_package']), ])
    hook_path = _generate_nuitka_runtime_hook()
    if SETTINGS['nuitka_paramas']['include_module']:
        args.extend(["--include-module=" + ','.join(
            SETTINGS['nuitka_paramas']['include_module'] + ["beetle_nuitka_hook", ]), ])
    if SETTINGS['nuitka_paramas']['nofollow_import']:
        args.extend(["--nofollow-import-to=" + ','.join(SETTINGS['nuitka_paramas']['nofollow_import']), ])
    args.extend(SETTINGS['nuitka_paramas']['extra_nuitka_args'])
    args.extend(extra_args)
    args.append(path(SETTINGS["main_module"]))
    makedirs(path('target/'), exist_ok=True)
    env = os.environ.copy()
    if 'PYTHONPATH' not in env:
        env['PYTHONPATH'] = ""
    env['PYTHONPATH'] = os.path.dirname(hook_path) + os.pathsep + env['PYTHONPATH']
    # 执行nuitka
    ret = run(args, env=env, check=True)
    if ret.returncode == 0:
        if debug:
            print(str(ret))
    else:
        print(str(ret))
        exit(1)

    output_dir = path("target/" + "main.dist")
    freeze_dir = path('${freeze_dir}')
    for loader, module_name, is_pkg in pkgutil.iter_modules():
        if is_pkg and module_name in SETTINGS['nuitka_paramas']['nofollow_import']:
            copy_module(loader.path, module_name, output_dir)
    if SETTINGS['nuitka_paramas']['need_dist_info']:
        if sys.version_info[0] == 3 and sys.version_info[1] >= 8:
            from importlib.metadata import distribution

            def copy_dist_info(dist_name, output_dir):
                dist = distribution(dist_name)
                src = str(dist._path)
                dst = os.path.join(output_dir, os.path.basename(src))
                print(f"copy {src} to {dst}")
                shutil.copytree(src, dst)

            for dist_name in SETTINGS['nuitka_paramas']['need_dist_info']:
                copy_dist_info(dist_name, output_dir)
        else:
            BeetleError(
                'The free version of beetle only supports Python >= 3.6'
            )
    # In most cases, rename(src, dst) silently "works" when src == dst. But on
    # some Windows drives, it raises a FileExistsError. So check src != dst:
    if PurePath(output_dir) != PurePath(freeze_dir):
        rename(output_dir, freeze_dir)


def _generate_nuitka_runtime_hook():
    makedirs(path('target/Nuitka'), exist_ok=True)
    module = beetle_runtime._frozen
    hook_path = path('target/Nuitka/beetle_nuitka_hook.py')
    with open(hook_path, 'w', encoding="utf-8") as f:
        # Inject public settings such as "version" into the binary, so
        # they're available at run time:
        f.write('\n'.join([
            'import importlib',
            'module = importlib.import_module(%r)' % module.__name__,
            'module.BUILD_SETTINGS = %r' % filter_public_settings(SETTINGS)
        ]))
    return hook_path


def copy_module(module_path, module_name, DIST_DIR):
    src = os.path.join(module_path, module_name)
    dst = os.path.join(DIST_DIR, module_name)
    print(f"copy {src} to {dst}")
    shutil.copytree(src, dst)


def run_pyinstaller(extra_args=None, debug=False):
    if extra_args is None:
        extra_args = []
    app_name = SETTINGS['app_name']
    # Would like log level WARN when not debugging. This works fine for
    # PyInstaller 3.3. However, for 3.4, it gives confusing warnings
    # "hidden import not found". So use ERROR instead.
    log_level = 'DEBUG' if debug else 'ERROR'
    args = [
        'pyinstaller',
        '--name', app_name,
        '--noupx',
        '--log-level', log_level,
        '--noconfirm'
    ]
    for hidden_import in SETTINGS['pyinstaller_paramas']['hidden_imports']:
        args.extend(['--hidden-import', hidden_import])
    args.extend(SETTINGS['pyinstaller_paramas']['extra_pyinstaller_args'])
    args.extend(extra_args)
    args.extend([
        '--distpath', path('target'),
        '--specpath', path('target/PyInstaller'),
        '--workpath', path('target/PyInstaller')
    ])
    args.extend(['--additional-hooks-dir', join(dirname(__file__), 'hooks')])
    if SETTINGS['pyinstaller_paramas'].get("additional_hooks_dir"):
        args.extend(['--additional-hooks-dir', os.path.join(SETTINGS['project_dir'], SETTINGS['pyinstaller_paramas']["additional_hooks_dir"])])
    if debug:
        args.extend(['--debug', 'all'])
        if is_mac():
            # Force generation of an .app bundle. Otherwise, PyInstaller skips
            # it when --debug is given.
            args.append('-w')
    hook_path = _generate_pyinstaller_runtime_hook()
    args.extend(['--runtime-hook', hook_path])
    args.append(path(SETTINGS['main_module']))
    run(args, check=True)
    output_dir = path('target/' + app_name + ('.app' if is_mac() else ''))
    freeze_dir = path('${freeze_dir}')
    # In most cases, rename(src, dst) silently "works" when src == dst. But on
    # some Windows drives, it raises a FileExistsError. So check src != dst:
    if PurePath(output_dir) != PurePath(freeze_dir):
        rename(output_dir, freeze_dir)


def _generate_pyinstaller_runtime_hook():
    makedirs(path('target/PyInstaller'), exist_ok=True)
    module = beetle_runtime._frozen
    hook_path = path('target/PyInstaller/beetle_pyinstaller_hook.py')
    with open(hook_path, 'w', encoding="utf-8") as f:
        # Inject public settings such as "version" into the binary, so
        # they're available at run time:
        f.write('\n'.join([
            'import importlib',
            'module = importlib.import_module(%r)' % module.__name__,
            'module.BUILD_SETTINGS = %r' % filter_public_settings(SETTINGS)
        ]))
    return hook_path


def _generate_medias():
    """
    Copy the data files from src/main/medias to ${freeze_dir}.
    Automatically filters files mentioned in the setting files_to_filter:
    Placeholders such as ${app_name} are automatically replaced by the
    corresponding setting in files on that list.
    """
    freeze_dir = path('${freeze_dir}')
    if is_mac():
        medias_dest_dir = join(freeze_dir, 'Contents', 'Resources')
    else:
        medias_dest_dir = freeze_dir

    for profile in LOADED_PROFILES:
        _copy(default_path, 'src/freeze/' + profile, freeze_dir)
        _copy(path, PROJECTINFO.medias_dir + profile, medias_dest_dir)
        _copy(path, PROJECTINFO.freeze_dir + profile, freeze_dir)

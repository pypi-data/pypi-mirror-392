from beetle import path
from beetle.freeze import _generate_medias, run_pyinstaller, run_nuitka, FreezeTool
from beetle_runtime.project import PROJECTINFO
from glob import glob
import os
from os import remove
from shutil import copy


def freeze_linux(debug=False, tool=FreezeTool.pyinstaller):
    if tool == FreezeTool.pyinstaller:
        freeze_linux_pyinstaller(debug=debug)
    else:
        freeze_linux_nuitka(debug=debug)


def freeze_linux_nuitka(debug=False):
    args = []
    args.extend(['--linux-icon=' + path(os.path.join(PROJECTINFO.icons_dir, 'Icon.ico')), ])
    run_nuitka(args, debug)
    _generate_medias()
    copy(path(os.path.join(PROJECTINFO.icons_dir, 'Icon.ico')), path('${freeze_dir}'))


def freeze_linux_pyinstaller(debug=False):
    run_pyinstaller(debug=debug)
    _generate_medias()
    copy(path(os.path.join(PROJECTINFO.icons_dir, 'Icon.ico')), path('${freeze_dir}'))
    # For some reason, PyInstaller packages libstdc++.so.6 even though it is
    # available on most Linux distributions. If we include it and run our app on
    # a different Ubuntu version, then Popen(...) calls fail with errors
    # "GLIBCXX_... not found" or "CXXABI_..." not found. So ensure we don't
    # package the file, so that the respective system's compatible version is
    # used:
    remove_shared_libraries(
        'libstdc++.so.*', 'libtinfo.so.*', 'libreadline.so.*', 'libdrm.so.*'
    )


def remove_shared_libraries(*filename_patterns):
    for pattern in filename_patterns:
        for file_path in glob(path('${freeze_dir}/' + pattern)):
            remove(file_path)

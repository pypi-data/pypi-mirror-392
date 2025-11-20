

from os.path import relpath, join
from setuptools import setup, find_packages

import os


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def _get_package_data(pkg_dir, data_subdir):
    result = []
    for dirpath, _, filenames in os.walk(join(pkg_dir, data_subdir)):
        for filename in filenames:
            filepath = join(dirpath, filename)
            result.append(relpath(filepath, pkg_dir))
    return result


description = 'Create cross-platform desktop applications with Python and Qt'
setup(
    name='qbeetle',
    # Also update beetle/_defaults/requirements/base.txt when you change this:
    version='0.0.4',
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Danqing Li',
    author_email='492847382@qq.com',
    url='https://beetle-tool.github.io/beetle-doc/',
    packages=find_packages(exclude=('tests', 'tests.*')),
    package_data={
        'beetle': _get_package_data('beetle', '_defaults') + _get_package_data('beetle', 'locale'),
        'beetle.builtin_commands':
            _get_package_data('beetle/builtin_commands', 'project_template'),
        'beetle.builtin_commands._gpg':
            ['Dockerfile', 'genkey.sh', 'gpg-agent.conf'],
        'beetle.installer.mac': _get_package_data(
            'beetle/installer/mac', 'create-dmg'
        ),
        'beetle_runtime': _get_package_data('beetle_runtime', 'locale'),
    },
    install_requires=['Nuitka>=1.8', 'GitPython', 'Babel', 'QtPy'],
    extras_require={
        # Also update requirements.txt when you change this:
        'licensing': ['rsa>=3.4.2'],
        'sentry': ['sentry-sdk>=0.6.6'],
        'upload': ['boto3']
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
    
        "License :: OSI Approved :: MIT License",
    
        'Operating System :: OS Independent',
    
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',

        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points={
        'console_scripts': ['beetle=beetle.__main__:_main']
    },
    keywords='PyQt5 PyQt6 PySide2 PySide6',
    platforms=['MacOS', 'Windows', 'Debian', 'Fedora', 'CentOS', 'Arch'],
    python_requires='>=3.8'
)

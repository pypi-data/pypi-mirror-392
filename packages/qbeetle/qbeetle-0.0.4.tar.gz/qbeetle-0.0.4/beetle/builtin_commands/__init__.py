"""
This module contains all of beetle's built-in commands. They are invoked when you
run `beetle <command>` on the command line. But you are also free to import them in
your Python build script and execute them there.
"""

from beetle.translate import _
from beetle import path, SETTINGS, activate_profile
from beetle.builtin_commands._util import prompt_for_value, is_valid_version, \
    require_project_existing, update_json, require_frozen_app, require_installer
from beetle.builtin_commands._template import get_templates_list, get_templates_dict, add_customer_template, \
    delete_customer_template, _update_template, BUILT_TEMPLATE_DIR, CUSTOMER_TEMPLATE_DIR
from beetle.cmdline import command
from beetle.resources import copy_with_filtering
from beetle.upload import _upload_repo
from beetle_runtime import BeetleError
from beetle_runtime.platform import is_windows, is_mac, is_linux, is_arch_linux, \
    is_ubuntu, is_fedora
from beetle_runtime.project import PROJECTINFO, get_project_json
from beetle.freeze import FreezeTool
from getpass import getuser
from importlib.util import find_spec
from os import listdir, remove, unlink, mkdir
from os.path import join, isfile, isdir, islink, dirname, exists, relpath
from shutil import rmtree
from unittest import TestSuite, TextTestRunner, defaultTestLoader

import logging
import os
import subprocess
import sys

_LOG = logging.getLogger(__name__)


@command
def template_list():
    templates_dict = get_templates_dict()
    if len(templates_dict["built"]) > 0:
        print(_("Built in templates:"))
        for template in templates_dict["built"]:
            print(f"    {template}")

    if len(templates_dict["customer"]) > 0:
        print(_("Customer adding templates:"))
        for template in templates_dict["customer"]:
            print(f"    {template}")


template_list.__doc__ = _(
    """A list of project templates in the repository"""
)


@command
def update_template():
    try:
        _update_template()
    except Exception as e:
        raise BeetleError(
            _("Failed to update template: \n") + str(e)
        )


update_template.__doc__ = _(
    """Update from Beetle's official project template repository to local project template repository"""
)


@command
def add_template():
    template_path = prompt_for_value(_('Project template path'))
    if os.path.isdir(template_path):
        add_customer_template(template_path)
    else:
        raise BeetleError(
            _("The project template path does not exist!\n %s.\n") % template_path
        )


add_template.__doc__ = _(
    """Add a new customer-defined project template to Beetle"""
)


@command
def delete_template():
    customer_list = get_templates_dict()["customer"]

    template_name = prompt_for_value('Project Template Name:', choices=tuple(customer_list))
    if template_name:
        delete_customer_template(template_name)
    else:
        _LOG.info(
            _("No project template name provided, do nothing!")
        )


delete_template.__doc__ = _(
    """Delete Beetle's customer-defined project template。"""
)


@command
def startproject():
    templates_list = get_templates_list()

    project_template = prompt_for_value(
        _('Select a project template'), choices=tuple(templates_list)
    )

    if project_template:
        if project_template not in templates_list:
            raise BeetleError(
                "The project template with the name %s does not exist, \n    please choose a different name in %s." % (
                project_template, str(templates_list))
            )

        templates_dict = get_templates_dict()
        if project_template in templates_dict["built"]:
            template_dir = os.path.join(BUILT_TEMPLATE_DIR, project_template)
        else:
            template_dir = os.path.join(CUSTOMER_TEMPLATE_DIR, project_template)

        PROJECTINFO.init_project_info(path(template_dir))
    else:
        _LOG.info(
            _("No project template name provided, do nothing!")
        )
        return

    if exists(PROJECTINFO.source_dir):
        raise BeetleError(_('The directory (%s) already exists, abort the operation') % PROJECTINFO.source_dir)

    app = prompt_for_value('App Name', default='MyApp')
    user = getuser().title()
    author = prompt_for_value('Author', default=user)
    has_pyqt5 = _has_module('PyQt5')
    has_pyqt6 = _has_module('PyQt6')
    has_pyside2 = _has_module('PySide2')
    has_pyside6 = _has_module('PySide6')
    if has_pyqt5 and not has_pyside2 and not has_pyqt6 and not has_pyside6:
        python_bindings = 'PyQt5'
    elif has_pyqt6 and not has_pyside2 and not has_pyqt5 and not has_pyside6:
        python_bindings = 'PyQt6'
    elif has_pyside2 and not has_pyside6 and not has_pyqt5 and not has_pyqt6:
        python_bindings = 'PySide2'
    elif has_pyside6 and not has_pyside2 and not has_pyqt5 and not has_pyqt6:
        python_bindings = 'PySide6'
    else:
        python_bindings = prompt_for_value(
            'Qt bindings', choices=('PyQt5', 'PyQt6', 'PySide2', 'PySide6'), default='PyQt5'
        )
    eg_bundle_id = 'com.%s.%s' % (
        author.lower().split()[0], ''.join(app.lower().split())
    )
    mac_bundle_identifier = prompt_for_value(
        'Mac bundle identifier (eg. %s, optional)' % eg_bundle_id,
        optional=True
    )
    mkdir(PROJECTINFO.source_dir)
    template_path = lambda relpath: join(template_dir, *relpath.split('/'))

    files_to_filter_ = [template_path(file) for file in PROJECTINFO.files_to_filter]
    copy_with_filtering(
        template_dir, '.', {
            'app_name': app,
            'author': author,
            'mac_bundle_identifier': mac_bundle_identifier,
            'python_bindings': python_bindings
        },
        files_to_filter=files_to_filter_
    )

    update_json(path(get_project_json(os.getcwd())), {'qt_bindings': python_bindings})

    print('')
    _msg = _("""
    The %s/ directory has been created. If you already have %s installed, you can do so now:\n\n    beetle run
    """) % (PROJECTINFO.source_dir, python_bindings)
    _LOG.info(_msg)


startproject.__doc__ = _(
    """Start a new project in the current directory"""
)


@command
def run():
    require_project_existing()
    PROJECTINFO.init_project_info(path("."))
    if not _has_module('PyQt5') and not _has_module('PySide2') and not _has_module('PyQt6') and not _has_module(
            'PySide6'):
        raise BeetleError(_(
            "The PyQt5 or PySide2 or PyQt6 or PySide6 could not be found. Maybe you need to::\n"
            "    pip install PyQt5==5.9.2 or\n"
            "    pip install PySide2==5.12.2"
        ))
    env = dict(os.environ)
    pythonpath = path('./')
    old_pythonpath = env.get('PYTHONPATH', '')
    if old_pythonpath:
        pythonpath += os.pathsep + old_pythonpath
    env['PYTHONPATH'] = pythonpath
    subprocess.run([sys.executable, path(SETTINGS['main_module'])], env=env)


run.__doc__ = _(
    """Run your app from source"""
)


@command
def freeze(debug=False):
    require_project_existing()
    PROJECTINFO.init_project_info(path("."))
    ToolList = [member for member in FreezeTool]

    tool = prompt_for_value(
        _('Select a Compile tool'), choices=tuple(ToolList)
    )

    if tool not in ToolList:
        raise BeetleError(
            _("%s is not allowed, you can select one from %s.") % (tool, str(ToolList))
        )

    if tool == FreezeTool.pyinstaller:
        if not _has_module('PyInstaller'):
            raise BeetleError(_(
                "Can't find PyInstaller, maybe you need to:\n"
                "    pip install PyInstaller"
            ))
    else:
        if not _has_module('nuitka'):
            raise BeetleError(
                "Can't find nuitka, maybe you need to:\n"
                "    pip install nuitka>=1.8"
            )
    version = SETTINGS['version']
    if not is_valid_version(version):
        raise BeetleError(_(
            'Invalid version detected in settings. It should be three\n'
            'numbers separated by dots, such as "1.2.3". You have:\n\t"%s".\n'
            'Usually, this can be fixed in %s.') % (version, PROJECTINFO.base_json)
                          )
    # Import respective functions late to avoid circular import

    app_name = SETTINGS['app_name']
    if is_mac():
        from beetle.freeze.mac import freeze_mac
        freeze_mac(debug=debug, tool=tool)
        executable = 'target/%s.app/Contents/MacOS/%s' % (app_name, app_name)
    else:
        executable = join('target', app_name, app_name)
        if is_windows():
            from beetle.freeze.windows import freeze_windows
            freeze_windows(debug=debug, tool=tool)
            executable += '.exe'
        elif is_linux():
            if is_ubuntu():
                from beetle.freeze.ubuntu import freeze_ubuntu
                freeze_ubuntu(debug=debug, tool=tool)
            elif is_arch_linux():
                from beetle.freeze.arch import freeze_arch
                freeze_arch(debug=debug, tool=tool)
            elif is_fedora():
                from beetle.freeze.fedora import freeze_fedora
                freeze_fedora(debug=debug, tool=tool)
            else:
                from beetle.freeze.linux import freeze_linux
                freeze_linux(debug=debug, tool=tool)
        else:
            raise BeetleError(_('Unsupported OS'))
    _LOG.info(
        _("Done. You can now run `%s`. "), executable
    )


freeze.__doc__ = _(
    """Compile your code to a standalone executable"""
)


@command
def sign():
    require_project_existing()
    PROJECTINFO.init_project_info(path("."))
    require_frozen_app()
    if is_windows():
        from beetle.sign.windows import sign_windows
        sign_windows()
        _LOG.info(
            _('Signed all binary files in %s and its subdirectories.'),
            relpath(path('${freeze_dir}'), path('.'))
        )
    elif is_mac():
        _LOG.info(_('beetle does not yet implement `sign` on macOS.'))
    else:
        _LOG.info(_('This platform does not support signing frozen apps.'))


sign.__doc__ = _(
    """Sign your app, so the user's OS trusts it"""
)


@command
def installer():
    require_project_existing()
    PROJECTINFO.init_project_info(path("."))
    require_frozen_app()
    linux_distribution_not_supported_msg = _(
        "Your Linux distribution is not supported, sorry. "
        "You can run `beetle buildvm` followed by `beetle runvm` to start a Docker "
        "VM of a supported distribution.")
    try:
        installer_fname = SETTINGS['installer']
    except KeyError:
        if is_linux():
            raise BeetleError(linux_distribution_not_supported_msg)
        raise
    out_file = join('target', installer_fname)
    msg_parts = ['Created %s.' % out_file]
    if is_windows():
        from beetle.installer.windows import create_installer_windows
        create_installer_windows()
    elif is_mac():
        from beetle.installer.mac import create_installer_mac
        create_installer_mac()
    elif is_linux():
        app_name = SETTINGS['app_name']
        if is_ubuntu():
            from beetle.installer.ubuntu import create_installer_ubuntu
            create_installer_ubuntu()
            install_cmd = 'sudo dpkg -i ' + out_file
            remove_cmd = 'sudo dpkg --purge ' + app_name
        elif is_arch_linux():
            from beetle.installer.arch import create_installer_arch
            create_installer_arch()
            install_cmd = 'sudo pacman -U ' + out_file
            remove_cmd = 'sudo pacman -R ' + app_name
        elif is_fedora():
            from beetle.installer.fedora import create_installer_fedora
            create_installer_fedora()
            install_cmd = 'sudo dnf install ' + out_file
            remove_cmd = 'sudo dnf remove ' + app_name
        else:
            raise BeetleError(linux_distribution_not_supported_msg)
        msg_parts.append(_(
            'You can for instance install it via the following command:\n'
            '    %s\n'
            'This places it in /opt/%s. To uninstall it again, you can use:\n'
            '    %s')
                         % (install_cmd, app_name, remove_cmd)
                         )
    else:
        raise BeetleError(_('Unsupported OS'))
    _LOG.info(' '.join(msg_parts))


installer.__doc__ = _(
    """Create an installer for your app"""
)


@command
def sign_installer():
    require_project_existing()
    PROJECTINFO.init_project_info(path("."))
    if is_mac():
        _LOG.info(_('beetle does not yet implement `sign_installer` on macOS.'))
        return
    if is_ubuntu():
        _LOG.info(_('Ubuntu does not support signing installers.'))
        return
    require_installer()
    if is_windows():
        from beetle.sign_installer.windows import sign_installer_windows
        sign_installer_windows()
    elif is_arch_linux():
        from beetle.sign_installer.arch import sign_installer_arch
        sign_installer_arch()
    elif is_fedora():
        from beetle.sign_installer.fedora import sign_installer_fedora
        sign_installer_fedora()
    _LOG.info('Signed %s.', join('target', SETTINGS['installer']))


sign_installer.__doc__ = _(
    """Sign installer, so the user's OS trusts it"""
)


def repo():
    require_project_existing()
    PROJECTINFO.init_project_info(path("."))
    require_project_existing()
    if not _repo_is_supported():
        raise BeetleError('This command is not supported on this platform.')
    app_name = SETTINGS['app_name']
    pkg_name = app_name.lower()
    try:
        gpg_key = SETTINGS['gpg_key']
    except KeyError:
        raise BeetleError(
            'GPG key for code signing is not configured. You might want to '
            'either\n'
            '    1) run `beetle gengpgkey` or\n'
            '    2) set "gpg_key" and "gpg_pass" in src/build/settings/.'
        )
    if is_ubuntu():
        from beetle.repo.ubuntu import create_repo_ubuntu
        if not SETTINGS['description']:
            _LOG.info(
                'Hint: Your app\'s "description" is empty. Consider setting it '
                'in src/build/settings/linux.json.'
            )
        create_repo_ubuntu()
        _LOG.info(
            'Done. You can test the repository with the following commands:\n'
            '    echo "deb [arch=amd64] file://%s stable main" '
            '| sudo tee /etc/apt/sources.list.d/%s.list\n'
            '    sudo apt-key add %s\n'
            '    sudo apt-get update\n'
            '    sudo apt-get install %s\n'
            'To revert these changes:\n'
            '    sudo dpkg --purge %s\n'
            '    sudo apt-key del %s\n'
            '    sudo rm /etc/apt/sources.list.d/%s.list\n'
            '    sudo apt-get update',
            path('target/repo'), pkg_name,
            path('src/sign/linux/public-key.gpg'), pkg_name, pkg_name, gpg_key,
            pkg_name,
            extra={'wrap': False}
        )
    elif is_arch_linux():
        from beetle.repo.arch import create_repo_arch
        create_repo_arch()
        _LOG.info(
            "Done. You can test the repository with the following commands:\n"
            "    sudo cp /etc/pacman.conf /etc/pacman.conf.bu\n"
            "    echo -e '\\n[%s]\\nServer = file://%s' "
            "| sudo tee -a /etc/pacman.conf\n"
            "    sudo pacman-key --add %s\n"
            "    sudo pacman-key --lsign-key %s\n"
            "    sudo pacman -Syu %s\n"
            "To revert these changes:\n"
            "    sudo pacman -R %s\n"
            "    sudo pacman-key --delete %s\n"
            "    sudo mv /etc/pacman.conf.bu /etc/pacman.conf",
            app_name, path('target/repo'),
            path('src/sign/linux/public-key.gpg'), gpg_key, pkg_name, pkg_name,
            gpg_key,
            extra={'wrap': False}
        )
    else:
        assert is_fedora()
        from beetle.repo.fedora import create_repo_fedora
        create_repo_fedora()
        _LOG.info(
            "Done. You can test the repository with the following commands:\n"
            "    sudo rpm -v --import %s\n"
            "    sudo dnf config-manager --add-repo file://%s/target/repo\n"
            "    sudo dnf install %s\n"
            "To revert these changes:\n"
            "    sudo dnf remove %s\n"
            "    sudo rm /etc/yum.repos.d/*%s*.repo\n"
            "    sudo rpm --erase gpg-pubkey-%s",
            path('src/sign/linux/public-key.gpg'), SETTINGS['project_dir'],
            pkg_name, pkg_name, app_name, gpg_key[-8:].lower(),
            extra={'wrap': False}
        )


repo.__doc__ = _("Generate files for automatic updates")


def _repo_is_supported():
    return is_ubuntu() or is_arch_linux() or is_fedora()


def upload():
    """
    Upload installer and repository to fbs.sh
    """
    require_project_existing()
    PROJECTINFO.init_project_info(path("."))
    try:
        username = SETTINGS['fbs_user']
        password = SETTINGS['fbs_pass']
    except KeyError as e:
        raise BeetleError(
            'Could not find setting "%s". You may want to invoke one of the '
            'following:\n'
            ' * beetle register\n'
            ' * beetle login'
            % (e.args[0],)
        ) from None
    _upload_repo(username, password)
    app_name = SETTINGS['app_name']
    url = lambda p: 'https://fbs.sh/%s/%s/%s' % (username, app_name, p)
    message = 'Done! '
    pkg_name = app_name.lower()
    installer_url = url(SETTINGS['installer'])
    if is_linux():
        message += 'Your users can now install your app via the following ' \
                   'commands:\n'
        format_commands = lambda *cmds: '\n'.join('    ' + c for c in cmds)
        repo_url = url(SETTINGS['repo_subdir'])
        if is_ubuntu():
            message += format_commands(
                "sudo apt-get install apt-transport-https",
                "wget -qO - %s | sudo apt-key add -" % url('public-key.gpg'),
                "echo 'deb [arch=amd64] %s stable main' | " % repo_url +
                "sudo tee /etc/apt/sources.list.d/%s.list" % pkg_name,
                "sudo apt-get update",
                "sudo apt-get install " + pkg_name
            )
            message += '\nIf they already have your app installed, they can ' \
                       'force an immediate update via:\n'
            message += format_commands(
                'sudo apt-get update '
                '-o Dir::Etc::sourcelist="/etc/apt/sources.list.d/%s.list" '
                '-o Dir::Etc::sourceparts="-" -o APT::Get::List-Cleanup="0"'
                % pkg_name,
                'sudo apt-get install --only-upgrade ' + pkg_name
            )
        elif is_arch_linux():
            message += format_commands(
                "curl -O %s && " % url('public-key.gpg') +
                "sudo pacman-key --add public-key.gpg && " +
                "sudo pacman-key --lsign-key %s && " % SETTINGS['gpg_key'] +
                "rm public-key.gpg",
                "echo -e '\\n[%s]\\nServer = %s' | sudo tee -a /etc/pacman.conf"
                % (app_name, repo_url),
                "sudo pacman -Syu " + pkg_name
            )
            message += '\nIf they already have your app installed, they can ' \
                       'force an immediate update via:\n'
            message += format_commands('sudo pacman -Syu --needed ' + pkg_name)
        elif is_fedora():
            message += format_commands(
                "sudo rpm -v --import " + url('public-key.gpg'),
                "sudo dnf config-manager --add-repo %s/%s.repo"
                % (repo_url, app_name),
                "sudo dnf install " + pkg_name
            )
            message += "\n(On CentOS, replace 'dnf' by 'yum' and " \
                       "'dnf config-manager' by 'yum-config-manager'.)"
            message += '\nIf they already have your app installed, they can ' \
                       'force an immediate update via:\n'
            message += \
                format_commands('sudo dnf upgrade %s --refresh' % pkg_name)
            message += '\nThis is for Fedora. For CentOS, use:\n'
            message += format_commands(
                'sudo yum clean all && sudo yum upgrade ' + pkg_name
            )
        else:
            raise BeetleError('This Linux distribution is not supported.')
        message += '\nFinally, your users can also install without automatic ' \
                   'updates by downloading:\n    ' + installer_url
        extra = {'wrap': False}
    else:
        message += 'Your users can now download and install %s.' % installer_url
        extra = None
    _LOG.info(message, extra=extra)


upload.__doc__ = _("Upload installer and repository to fbs.sh")


def release(version=None):
    require_project_existing()
    PROJECTINFO.init_project_info(path("."))
    if version is None:
        curr_version = SETTINGS['version']
        next_version = _get_next_version(curr_version)
        release_version = prompt_for_value(
            'Release version', default=next_version
        )
    elif version == 'current':
        release_version = SETTINGS['version']
    else:
        release_version = version
    if not is_valid_version(release_version):
        if not is_valid_version(version):
            raise BeetleError(
                _('The release version of your app is invalid. It should be '
                  'three\nnumbers separated by dots, such as "1.2.3". '
                  'You have: "%s".') % release_version
            )
    activate_profile('release')
    SETTINGS['version'] = release_version
    log_level = _LOG.level
    if log_level == logging.NOTSET:
        _LOG.setLevel(logging.WARNING)
    try:
        clean()
        freeze()
        if is_windows() and _has_windows_codesigning_certificate():
            sign()
        installer()
        if (is_windows() and _has_windows_codesigning_certificate()) or \
                is_arch_linux() or is_fedora():
            sign_installer()
        if _repo_is_supported():
            repo()
    finally:
        _LOG.setLevel(log_level)
    upload()
    base_json = PROJECTINFO.base_json
    update_json(path(base_json), {'version': release_version})
    _LOG.info(_('Also, %s was updated with the new version.'), base_json)


release.__doc__ = _("Bump version and run clean,freeze,...,upload")


@command
def test():
    require_project_existing()
    PROJECTINFO.init_project_info(path("."))
    sys.path.append(path('src/main/python'))
    suite = TestSuite()
    test_dirs = SETTINGS['test_dirs']
    for test_dir in map(path, test_dirs):
        sys.path.append(test_dir)
        try:
            dir_names = listdir(test_dir)
        except FileNotFoundError:
            continue
        for dir_name in dir_names:
            dir_path = join(test_dir, dir_name)
            if isfile(join(dir_path, '__init__.py')):
                suite.addTest(defaultTestLoader.discover(
                    dir_name, top_level_dir=test_dir
                ))
    has_tests = bool(list(suite))
    if has_tests:
        TextTestRunner().run(suite)
    else:
        _LOG.warning(
            _('No tests found. You can add them to:\n * ') +
            '\n * '.join(test_dirs)
        )


test.__doc__ = _(
    """Execute your automated tests"""
)


@command
def clean():
    try:
        rmtree(path('target'))
    except FileNotFoundError:
        return
    except OSError:
        # In a docker container, target/ may be mounted so we can't delete it.
        # Delete its contents instead:
        for f in listdir(path('target')):
            fpath = join(path('target'), f)
            if isdir(fpath):
                rmtree(fpath, ignore_errors=True)
            elif isfile(fpath):
                remove(fpath)
            elif islink(fpath):
                unlink(fpath)


clean.__doc__ = _(
    """Remove previous build outputs"""
)


def _has_windows_codesigning_certificate():
    assert is_windows()
    from beetle.sign.windows import _CERTIFICATE_PATH
    return exists(path(_CERTIFICATE_PATH))


def _has_module(name):
    return bool(find_spec(name))


def _get_next_version(version):
    version_parts = version.split('.')
    next_patch = str(int(version_parts[-1]) + 1)
    return '.'.join(version_parts[:-1]) + '.' + next_patch

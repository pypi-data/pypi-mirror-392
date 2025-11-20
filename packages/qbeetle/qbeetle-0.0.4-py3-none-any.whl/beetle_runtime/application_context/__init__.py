
from typing import List
from collections import namedtuple
from beetle_runtime import _state, _frozen, _source
from beetle_runtime._resources import ResourceLocator
from beetle_runtime._signal import SignalWakeupHandler
from beetle_runtime.excepthook import _Excepthook, StderrExceptionHandler
from beetle_runtime.platform import is_windows, is_mac
from beetle_runtime.logger import Logger
from functools import lru_cache

import os
import sys
from pathlib import Path

from qtpy.QtCore import QIODevice, QSharedMemory
from qtpy.QtCore import Signal
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QApplication
from qtpy.QtNetwork import QAbstractSocket, QLocalServer, QLocalSocket


def cached_property(getter):
    """
    A cached Python @property. You use it in conjunction with ApplicationContext
    below to instantiate the components that comprise your application. For more
    information, please consult the Manual:
        https://build-system.fman.io/manual/#cached_property
    """
    return property(lru_cache()(getter))


class ApplicationContext:
    """
    The main point of contact between your application and beetle. For information
    on how to use it, please see the Manual:
        https://build-system.fman.io/manual/#your-python-code
    """

    def __init__(self, use_singleton=True):
        self.use_singleton = use_singleton
        if self.excepthook:
            self.excepthook.install()
        # Many Qt classes require a QApplication to have been instantiated.
        # Do this here, before everything else, to achieve this:
        self.app
        # We don't build as a console app on Windows, so no point in installing
        # the SIGINT handler:
        if not is_windows():
            self._signal_wakeup_handler = \
                SignalWakeupHandler(self.app, QAbstractSocket)
            self._signal_wakeup_handler.install()
        if self.app_icon:
            self.app.setWindowIcon(self.app_icon)

    def run(self):
        """
        You should overwrite this method with the steps for starting your app.
        See eg. beetle's tutorial.
        """
        raise NotImplementedError()

    @cached_property
    def app(self):
        """
        The global Qt QApplication object for your app. Feel free to overwrite
        this property, eg. if you wish to use your own subclass of QApplication.
        An example of this is given in the Manual.
        """

        if is_nuitka_frozen():
            import beetle_nuitka_hook

        if is_frozen():
            app_dir = os.path.dirname(sys.executable)
            log_folder = Path(app_dir)
        else:
            log_folder = Path(self._project_dir)

        log_folder = log_folder / "log"
        logger = Logger("application", log_folder)

        if self.use_singleton:
            application = SingletonApplication([], self.build_settings['app_name'], logger)
        else:
            application = QApplication([])
            application.logger = logger
        application.setApplicationName(self.build_settings['app_name'])
        application.setApplicationVersion(self.build_settings['version'])
        return application

    @cached_property
    def build_settings(self):
        """
        This dictionary contains the values of the settings listed in setting
        "public_settings". Eg. `self.build_settings['version']`.
        """
        if is_frozen():
            return _frozen.load_build_settings()
        return _source.load_build_settings(self._project_dir)

    def get_resource(self, *rel_path):
        """
        Return the absolute path to the data file with the given name or
        (relative) path. When running from source, searches src/main/resources.
        Otherwise, searches your app's installation directory. If no file with
        the given name or path exists, a FileNotFoundError is raised.
        """
        return self._resource_locator.locate(*rel_path)

    @cached_property
    def exception_handlers(self):
        """
        Return a list of exception handlers that should be invoked when an error
        occurs. See the documentation of module `beetle_runtime.excepthook` for
        more information.
        """
        return [StderrExceptionHandler()]

    @cached_property
    def licensing(self):
        """
        This field helps you implement a license key functionality for your
        application. For more information, see:
            https://build-system.fman.io/manual#license-keys
        """

        # beetle's licensing implementation incurs a dependency on Python library
        # `rsa`. We don't want to force all users to install this library.
        # So we import beetle_runtime.licensing here, instead of at the top of this
        # file. This lets people who don't use licensing avoid the dependency.
        from beetle_runtime.licensing import _Licensing

        return _Licensing(self.build_settings['licensing_pubkey'])

    @cached_property
    def app_icon(self):
        """
        The app icon. Not available on Mac because app icons are handled by the
        OS there.
        """
        if not is_mac():
            return QIcon(self.get_resource('Icon.ico'))

    @cached_property
    def excepthook(self):
        """
        Overwrite this method to use a custom excepthook. It should be an object
        with a .install() method, or `None` if you want to completely disable
        beetle's excepthook implementation.
        """
        return _Excepthook(self.exception_handlers)

    @cached_property
    def _resource_locator(self):
        if is_frozen():
            resource_dirs = _frozen.get_resource_dirs()
        else:
            resource_dirs = _source.get_resource_dirs(self._project_dir)
        return ResourceLocator(resource_dirs)

    @cached_property
    def _project_dir(self):
        assert not is_frozen(), 'Only available when running from source'
        return _source.get_project_dir()


class SingletonApplication(QApplication):
    """ Singleton application """

    messageSig = Signal(object)
    # logger = Logger("application")

    def __init__(self, argv: List[str], app_name: str, logger: Logger):
        super().__init__(argv)
        self.key = app_name
        self.logger = logger
        self.timeout = 1000
        self.server = QLocalServer(self)

        # cleanup (only needed for unix)
        QSharedMemory(app_name).attach()
        self.memory = QSharedMemory(self)
        self.memory.setKey(app_name)

        if self.memory.attach():
            self.isRunning = True
            self.sendMessage(argv[1] if len(argv) > 1 else 'show')
            self.logger.info(
                f"Another {app_name} is already running, you should kill it first to launch a new one.")
            sys.exit(1)

        self.isRunning = False
        if not self.memory.create(1):
            self.logger.error(self.memory.errorString())
            raise RuntimeError(self.memory.errorString())

        self.server.newConnection.connect(self.__onNewConnection)
        self.server.listen(app_name)

    def __onNewConnection(self):
        socket = self.server.nextPendingConnection()
        if socket.waitForReadyRead(self.timeout):
            # signalBus.appMessageSig.emit(
            #     socket.readAll().data().decode('utf-8'))
            socket.disconnectFromServer()

    def sendMessage(self, message: str):
        """ send message to another application """
        if not self.isRunning:
            return

        # connect to another application
        socket = QLocalSocket(self)
        socket.connectToServer(self.key, QIODevice.WriteOnly)
        if not socket.waitForConnected(self.timeout):
            self.logger.error(socket.errorString())
            return

        # send message
        socket.write(message.encode("utf-8"))
        if not socket.waitForBytesWritten(self.timeout):
            self.logger.error(socket.errorString())
            return

        socket.disconnectFromServer()


def is_frozen():
    """
    Return True if running from the frozen (i.e. compiled form) of your app, or
    False when running from source.
    """
    return getattr(sys, 'frozen', False) or "__compiled__" in globals()


def is_nuitka_frozen():
    """
    Return True if running from the nuitka frozen (i.e. nuitka compiled form) of your app, or
    False when running from source or PyInstaller frozen.
    """
    return "__compiled__" in globals()


def get_application_context(DevelopmentAppCtxtCls, FrozenAppCtxtCls=None):
    if FrozenAppCtxtCls is None:
        FrozenAppCtxtCls = DevelopmentAppCtxtCls
    if _state.APPLICATION_CONTEXT is None:
        _state.APPLICATION_CONTEXT = \
            FrozenAppCtxtCls() if is_frozen() else DevelopmentAppCtxtCls()
    return _state.APPLICATION_CONTEXT

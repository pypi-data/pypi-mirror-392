from beetle.freeze import FreezeTool
from beetle.freeze.linux import freeze_linux


def freeze_arch(debug=False, tool=FreezeTool.pyinstaller):
    freeze_linux(debug, tool=tool)

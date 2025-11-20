import os
import stat
import json
import git
import shutil
from copy import deepcopy
from beetle_runtime import BeetleError
from beetle_runtime._settings import _merge
from beetle_runtime.project import get_project_info

BASE_DIR = os.path.expanduser("~/.beetle/")
TEMPLATE_DIR = os.path.join(BASE_DIR, "template")
BUILT_TEMPLATE_DIR = os.path.join(TEMPLATE_DIR, "beetle_template")
CUSTOMER_TEMPLATE_DIR = os.path.join(TEMPLATE_DIR, "customer_template")
TEMPLATE_REPOSITORY_URL = "https://gitee.com/beetle-tool/beetle_template.git"
TAG = 'v1.0'


def readonly_handler(func, path, execinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def _update_template():
    global TAG, TEMPLATE_DIR, BUILT_TEMPLATE_DIR
    if os.path.isdir(TEMPLATE_DIR):
        shutil.rmtree(TEMPLATE_DIR, onerror=readonly_handler)
        os.makedirs(TEMPLATE_DIR)
    if not os.path.isdir(BUILT_TEMPLATE_DIR):
        repo = git.Repo.clone_from(url=TEMPLATE_REPOSITORY_URL, to_path=BUILT_TEMPLATE_DIR)
    else:
        repo = git.Repo(BUILT_TEMPLATE_DIR)
        if repo.is_dirty():
            repo.index.checkout(force=True)
        remote = repo.remote(name='origin')
        remote.pull()
    repo.git.checkout(TAG)


def get_templates_dict():
    return dict(
        built=_read_template_info(BUILT_TEMPLATE_DIR)["template_list"],
        customer=_read_template_info(CUSTOMER_TEMPLATE_DIR)["template_list"]
    )


def get_templates_list():
    return _read_template_info(BUILT_TEMPLATE_DIR)["template_list"] + \
           _read_template_info(CUSTOMER_TEMPLATE_DIR)["template_list"]


def add_customer_template(template_path):
    """
    添加 客户自定义项目模板
    :param template_path:
    :return:
    """
    # 检查 “project_info”
    project_info = get_project_info(template_path)

    if not os.path.isdir(CUSTOMER_TEMPLATE_DIR):
        os.makedirs(CUSTOMER_TEMPLATE_DIR)

    templates_list = get_templates_list()

    template_name = os.path.basename(template_path)
    if template_name in templates_list:
        raise BeetleError(
            "The project template with the name %s already exists, "
            "please take a different name." % template_name
        )

    dest = os.path.join(CUSTOMER_TEMPLATE_DIR, template_name)
    dict_ = dict(template_list=[template_name, ])
    _update_template_info(CUSTOMER_TEMPLATE_DIR, dict_)
    shutil.copytree(template_path, dest)


def delete_customer_template(template_name):
    if not os.path.isdir(CUSTOMER_TEMPLATE_DIR):
        os.makedirs(CUSTOMER_TEMPLATE_DIR)

    template_info = _read_template_info(CUSTOMER_TEMPLATE_DIR)

    if "template_list" in template_info:
        if template_name in template_info["template_list"]:
            dest = os.path.join(CUSTOMER_TEMPLATE_DIR, template_name)
            template_info_new = deepcopy(template_info)
            template_info_new["template_list"].remove(template_name)
            _write_template_info(CUSTOMER_TEMPLATE_DIR, template_info_new)
            shutil.rmtree(dest, onerror=readonly_handler)
    else:
        raise BeetleError(
            "There is no template with a name that is %s.\n" % template_name
        )


def _update_template_info(path, dict_):
    template_info = _read_template_info(path)
    template_info = _merge(template_info, dict_)
    _write_template_info(path, template_info)


def _read_template_info(path):
    template_info_path = _template_info_path(path)
    if os.path.isfile(template_info_path):
        with open(template_info_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return dict(template_list=[])


def _write_template_info(path, dict_):
    template_info_path = _template_info_path(path)
    with open(template_info_path, 'w', encoding="utf-8") as f:
        json.dump(dict_, f, indent=2)


def _template_info_path(path):
    return os.path.join(path, 'template_info.json')


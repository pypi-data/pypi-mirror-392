import os
import json

from beetle_runtime import BeetleError


def get_project_json(project_dir):
    return os.path.join(project_dir, "project.json")


def get_project_info(project_dir):
    _json_path = get_project_json(project_dir)
    if not os.path.isfile(_json_path):
        raise BeetleError(
            "Could not find the project.json file. Are you in the right folder?\n"
        )
    try:
        with open(_json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise BeetleError(
            "Could not parse the project.json file. Are you in the right folder?\n"
        )


class ProjectInfo:
    __info = {}

    def init_project_info(self, project_dir):
        project_info = get_project_info(project_dir)
        self.__info = project_info
        self.check_settings_dir()
        self.check_files_to_filter()
        self.check_source_dir()
        self.check_statics_dir()
        self.check_medias_dir()
        self.check_freeze_dir()
        self.check_icons_dir()
        self.check_languages()
        self.check_i18n_dir()
        self.check_rcc_paramas()
        self.check_qt_bindings()

    def check_files_to_filter(self):
        if not "files_to_filter" in self.__info:
            raise BeetleError(
                "Could not find 'files_to_filter'  key in the project.json file. Are you in the right folder?\n"
            )

    def check_source_dir(self):
        if not "source_dir" in self.__info:
            raise BeetleError(
                "Could not find 'source_dir'  key in the project.json file. Are you in the right folder?\n"
            )

    def check_settings_dir(self):
        if not "settings_dir" in self.__info:
            raise BeetleError(
                "Could not find 'settings_dir'  key in the project.json file. Are you in the right folder?\n"
            )

    def check_statics_dir(self):
        if not "statics_dir" in self.__info:
            raise BeetleError(
                "Could not find 'statics_dir'  key in the project.json file. Are you in the right folder?\n"
            )

    def check_medias_dir(self):
        if not "medias_dir" in self.__info:
            raise BeetleError(
                "Could not find 'medias_dir'  key in the project.json file. Are you in the right folder?\n"
            )

    def check_freeze_dir(self):
        if not "freeze_dir" in self.__info:
            raise BeetleError(
                "Could not find 'freeze_dir'  key in the project.json file. Are you in the right folder?\n"
            )

    def check_icons_dir(self):
        if not "icons_dir" in self.__info:
            raise BeetleError(
                "Could not find 'icons_dir'  key in the project.json file. Are you in the right folder?\n"
            )

    def check_languages(self):
        if not "languages" in self.__info:
            raise BeetleError(
                "Could not find 'languages'  key in the project.json file. Are you in the right folder?\n"
            )

    def check_i18n_dir(self):
        if not "i18n_dir" in self.__info:
            raise BeetleError(
                "Could not find 'i18n_dir'  key in the project.json file. Are you in the right folder?\n"
            )

    def check_rcc_paramas(self):
        if not "rcc_paramas" in self.__info:
            raise BeetleError(
                "Could not find 'rcc_paramas'  key in the project.json file. Are you in the right folder?\n"
            )

    def check_qt_bindings(self):
        if not "qt_bindings" in self.__info:
            raise BeetleError(
                "Could not find 'qt_bindings'  key in the project.json file. Are you in the right folder?\n"
            )

    @property
    def source_dir(self):
        self.check_source_dir()
        return self.__info["source_dir"]

    @property
    def settings_dir(self):
        self.check_settings_dir()
        return self.__info["settings_dir"]

    @property
    def base_json(self):
        self.check_settings_dir()
        return os.path.join(self.__info["settings_dir"], "base.json")

    @property
    def secret_json(self):
        self.check_settings_dir()
        return os.path.join(self.__info["settings_dir"], "secret.json")

    @property
    def files_to_filter(self):
        self.check_files_to_filter()
        return self.__info["files_to_filter"]

    @property
    def statics_dir(self):
        self.check_statics_dir()
        return self.__info["statics_dir"]

    @property
    def medias_dir(self):
        self.check_medias_dir()
        return self.__info["medias_dir"]

    @property
    def freeze_dir(self):
        self.check_freeze_dir()
        return self.__info["freeze_dir"]

    @property
    def icons_dir(self):
        self.check_icons_dir()
        return self.__info["icons_dir"]

    @property
    def languages(self):
        self.check_languages()
        return self.__info["languages"]

    @property
    def i18n_dir(self):
        self.check_i18n_dir()
        return self.__info["i18n_dir"]

    @property
    def rcc_paramas(self):
        self.check_rcc_paramas()
        return self.__info["rcc_paramas"]

    @property
    def qt_bindings(self):
        self.check_qt_bindings()
        return self.__info["qt_bindings"]


PROJECTINFO = ProjectInfo()

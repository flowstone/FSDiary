import configparser
import os
from io import StringIO

from loguru import logger

from src.const.fs_constants import FsConstants
from src.util.common_util import CommonUtil


class IniUtil:
    ##############Settings START################
    SETTINGS_KEY = "Settings"
    APP_MINI_MASK_CHECKED_KEY = "mini.mask_checked"
    APP_MINI_CHECKED_KEY = "mini.checked"
    APP_MINI_SIZE_KEY = "mini.size"
    APP_MINI_IMAGE_KEY = "mini.image"

    APP_TRAY_MENU_CHECKED_KEY = "tray_menu.checked"
    APP_TRAY_MENU_IMAGE_KEY = "tray_menu.image"

    WEBDAV_AUTO_CHECKED_KEY = "sync.webdav.auto_checked"
    WEBDAV_ADDRESS_KEY = "sync.webdav.address"
    WEBDAV_USERNAME_KEY = "sync.webdav.username"
    WEBDAV_PASSWORD_KEY = "sync.webdav.password"
    WEBDAV_REMOTE_DIR_KEY = "sync.webdav.remote_dir"
    WEBDAV_LOCAL_DIR_KEY = "sync.webdav.local_dir"
    ##############Settings END#################


    def __init__(self):
        pass

    # 从 INI 文件加载用设置
    @staticmethod
    def get_ini_config():
        """
        获取 INI 文件的配置对象，如果文件不存在则初始化。
        """
        ini_path = CommonUtil.get_app_ini_path()
        config = configparser.ConfigParser(allow_no_value=True)

        if not os.path.exists(ini_path):
            # 如果文件不存在，创建一个空配置文件
            with open(ini_path, "w", encoding="utf-8") as f:
                f.write("; 应用配置文件\n")
        else:
            config.read(ini_path, encoding="utf-8")
        return config, ini_path

    @staticmethod
    def get_config_param(section: str, key: str, fallback=None, as_type:any=str):
        """
        通用方法，从 INI 文件中读取指定的配置项。

        :param section: str, 配置节名称
        :param key: str, 配置项键名
        :param fallback: 默认值
        :param as_type: 返回值类型，支持 str、int、bool
        :return: 配置值
        """
        config, _ = IniUtil.get_ini_config()
        try:
            if as_type == bool:
                return config.getboolean(section, key, fallback=fallback)
            elif as_type == int:
                return config.getint(section, key, fallback=fallback)
            else:
                return config.get(section, key, fallback=fallback)
        except Exception as e:
            logger.error(f"读取配置项失败：[{section}] {key}, 错误：{e}")
            return fallback

    @staticmethod
    def set_config_param(section: str, key: str, value: str):
        """
        通用方法，更新 INI 文件中的指定配置项。

        :param section: str, 配置节名称
        :param key: str, 配置项键名
        :param value: str, 配置值
        """
        config, ini_path = IniUtil.get_ini_config()
        IniUtil.update_ini_line(ini_path, section, key, value)
        logger.info(f"配置已更新：[{section}] {key} = {value}")

    @staticmethod
    def get_ini_sync_webdav_parm(key: str):
        if IniUtil.WEBDAV_AUTO_CHECKED_KEY == key:
            return IniUtil.get_config_param(IniUtil.SETTINGS_KEY, key, fallback=False, as_type=bool)
        else:
            return IniUtil.get_config_param(IniUtil.SETTINGS_KEY, key, fallback="")


    @staticmethod
    def set_ini_sync_webdav_param(key: str, value: any):
        if type(value) == bool:
            IniUtil.set_config_param(IniUtil.SETTINGS_KEY, key, "true" if value else "false")
        else:
            IniUtil.set_config_param(IniUtil.SETTINGS_KEY, key, value)
        logger.info(f"WebDAV {key} 已更新为: {value}")

    @staticmethod
    def get_ini_app_param(key: str):
        if IniUtil.APP_MINI_MASK_CHECKED_KEY == key:
            return IniUtil.get_config_param(IniUtil.SETTINGS_KEY, key, fallback=True, as_type=bool)
        elif IniUtil.APP_MINI_CHECKED_KEY == key or IniUtil.APP_TRAY_MENU_CHECKED_KEY == key:
            return IniUtil.get_config_param(IniUtil.SETTINGS_KEY, key, fallback=False, as_type=bool)
        elif IniUtil.APP_MINI_SIZE_KEY == key:
            return IniUtil.get_config_param(IniUtil.SETTINGS_KEY, key, as_type=int)
        else:
            return IniUtil.get_config_param(IniUtil.SETTINGS_KEY, key)

    @staticmethod
    def set_ini_app_param(key: str, value: any):
        if type(value) == bool:
            IniUtil.set_config_param(IniUtil.SETTINGS_KEY, key, "true" if value else "false")
        elif type(value) == int:
            IniUtil.set_config_param(IniUtil.SETTINGS_KEY, key, str(value))
        else:
            IniUtil.set_config_param(IniUtil.SETTINGS_KEY, key, value)
        logger.info(f"{key}已更新为: {value}")


    @staticmethod
    def update_ini_line(ini_path, section, key, value):
        """
        在 INI 文件中修改指定配置项的值，仅修改目标行，保留其他内容（包括注释和空行）。

        :param ini_path: str, INI 文件路径。
        :param section: str, 目标配置节名称（如 "Flask"）。
        :param key: str, 配置项的键名（如 "flag"）。
        :param value: str, 配置项的新值。
        """
        if not os.path.exists(ini_path):
            raise FileNotFoundError(f"配置文件 {ini_path} 不存在！")

        with open(ini_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        updated = False
        in_target_section = False
        section_header = f"[{section}]"
        new_line = f"{key} = {value}\n"
        section_end_index = -1  # 初始化目标节的结束索引

        for i, line in enumerate(lines):
            stripped_line = line.strip()

            # 检测到目标节
            if stripped_line == section_header:
                in_target_section = True
                section_end_index = i  # 记录目标节的最后一行索引
                continue

            # 检测到目标键，并处于目标节
            if in_target_section and stripped_line.startswith(f"{key}"):
                lines[i] = new_line
                updated = True
                break

            # 检测到新节开始，退出目标节
            if in_target_section and stripped_line.startswith("[") and stripped_line != section_header:
                in_target_section = True
                section_end_index = i - 1  # 目标节的最后一行索引
                break

        # 如果没有找到目标键，添加到目标节末尾
        if not updated:
            if in_target_section:
                # 在目标节的末尾插入新键值对
                lines.insert(section_end_index + 1, new_line)
            else:
                # 如果没有找到目标节，新增节和键值对
                lines.append(f"\n{section_header}\n")
                lines.append(new_line)

        # 写回修改后的文件
        with open(ini_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
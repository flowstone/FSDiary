import configparser
import os
from io import StringIO

from loguru import logger

from src.const.fs_constants import FsConstants
from src.util.common_util import CommonUtil


class ConfigUtil:
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
    def get_ini_github_token():
        """
        从 INI 文件加载 Github Token
        """
        config, _ = ConfigUtil.get_ini_config()
        return config.get("Github", "token", fallback="")

    @staticmethod
    def get_ini_github_repo():
        """
        从 INI 文件加载 Github Repo
        """
        config, _ = ConfigUtil.get_ini_config()
        return config.get("Github", "repo", fallback="")

    @staticmethod
    def get_ini_github_base_folder():
        """
        从 INI 文件加载 Github Repo
        """
        config, _ = ConfigUtil.get_ini_config()
        return config.get("Github", "base_folder", fallback="")

    # 从 INI 文件读取 遮罩是否启用的配置
    @staticmethod
    def get_ini_mini_mask_checked():
        """
        从 INI 文件读取 遮罩是否启用的配置
        """
        config, _ = ConfigUtil.get_ini_config()
        return config.getboolean("Settings", "mini.mask_checked", fallback=True)

    @staticmethod
    def get_ini_mini_checked():
        """
        从 INI 文件读取 遮罩是否启用的配置
        """
        config, _ = ConfigUtil.get_ini_config()
        return config.getboolean("Settings", "mini.checked", fallback=False)

    @staticmethod
    def get_ini_mini_size():
        """
        从 INI 文件读取 遮罩是否启用的配置
        """
        config, _ = ConfigUtil.get_ini_config()
        mini_size =  config.getint("Settings", "mini.size", fallback=FsConstants.APP_MINI_SIZE)
        return mini_size if ConfigUtil.get_ini_mini_checked() else FsConstants.APP_MINI_SIZE

    @staticmethod
    def get_ini_mini_image():
        """
        从 INI 文件读取 遮罩是否启用的配置
        """
        config, _ = ConfigUtil.get_ini_config()
        mini_image =  config.get("Settings", "mini.image", fallback=CommonUtil.get_mini_ico_full_path())
        # 如果悬浮球修改未启用，返回默认悬浮球图标
        if ConfigUtil.get_ini_mini_checked():
            # 如果悬浮球背景图片存在，返回图片路径，否则返回默认悬浮球图标
            return mini_image if os.path.exists(mini_image) else CommonUtil.get_mini_ico_full_path()
        else:
            return CommonUtil.get_mini_ico_full_path()

    @staticmethod
    def get_ini_tray_menu_checked():
        """
        从 INI 文件读取 遮罩是否启用的配置
        """
        config, _ = ConfigUtil.get_ini_config()
        return config.getboolean("Settings", "tray_menu.checked", fallback=False)

    @staticmethod
    def get_ini_tray_menu_image():
        """
        从 INI 文件读取 遮罩是否启用的配置
        """
        config, _ = ConfigUtil.get_ini_config()
        tray_menu_image =  config.get("Settings", "tray_menu.image", fallback=CommonUtil.get_resource_path(FsConstants.APP_BAR_ICON_FULL_PATH))
        # 如果托盘图标修改未启用，返回默认托盘图标
        if ConfigUtil.get_ini_tray_menu_checked():
            # 如果托盘图标图片存在，返回图片路径，否则返回默认托盘图标
            return tray_menu_image if os.path.exists(tray_menu_image) else CommonUtil.get_resource_path(FsConstants.APP_BAR_ICON_FULL_PATH)
        else:
            return CommonUtil.get_resource_path(FsConstants.APP_BAR_ICON_FULL_PATH)


    # 将应用可见性写入到 INI 配置文件中
    @staticmethod
    def set_ini_github_token(token):
        """
        将 Flask 服务的启用状态写入到 INI 配置文件中，保留注释。
        :param token: str, 。
        """
        config, ini_path = ConfigUtil.get_ini_config()
        # 更新配置值
        ConfigUtil.update_ini_line(ini_path, "Github", "token", token)
        logger.info(f"Github Token 已更新为: {token}")


    @staticmethod
    def set_ini_github_repo(repo):
        """
        将 应用字体加粗的启用状态写入到 INI 配置文件中，保留注释。
        :param repo: str, True 表示启用 应用字体加粗，False 表示禁用。
        """
        config, ini_path = ConfigUtil.get_ini_config()
        # 更新配置值
        ConfigUtil.update_ini_line(ini_path, "Github", "repo", repo)
        logger.info(f"Github Repo 已更新为: {repo}")

    @staticmethod
    def set_ini_github_base_folder(repo):
        """
        将 应用字体加粗的启用状态写入到 INI 配置文件中，保留注释。
        :param repo: str, True 表示启用 应用字体加粗，False 表示禁用。
        """
        config, ini_path = ConfigUtil.get_ini_config()
        # 更新配置值
        ConfigUtil.update_ini_line(ini_path, "Github", "base_folder", repo)
        logger.info(f"Github 根目录已更新为: {repo}")
    # 从 INI 文件读取 遮罩是否启用的配置
    @staticmethod
    def set_ini_mini_mask_checked(enabled):
        """
        将 遮罩动画的启用状态写入到 INI 配置文件中，保留注释。
        :param enabled: bool, True 表示启用 遮罩动画，False 表示禁用。
        """
        config, ini_path = ConfigUtil.get_ini_config()
        # 更新配置值
        ConfigUtil.update_ini_line(ini_path, "Settings", "mini.mask_checked", "true" if enabled else "false")
        logger.info(f"遮罩状态已更新为: {'启用' if enabled else '禁用'}")
    @staticmethod
    def set_ini_mini_checked(enabled):
        """
        将 悬浮球修改状态写入到 INI 配置文件中，保留注释。
        :param enabled: bool, True 表示启用 悬浮球修改，False 表示禁用。
        """
        config, ini_path = ConfigUtil.get_ini_config()
        # 更新配置值
        ConfigUtil.update_ini_line(ini_path, "Settings", "mini.checked", "true" if enabled else "false")
        logger.info(f"悬浮球状态已更新为: {'启用' if enabled else '禁用'}")


    @staticmethod
    def set_ini_mini_size(size: int):
        """
        将 悬浮球大小写入到 INI 配置文件中，保留注释。
        :param size: int, 悬浮球大小。
        """
        config, ini_path = ConfigUtil.get_ini_config()
        # 更新配置值
        ConfigUtil.update_ini_line(ini_path, "Settings", "mini.size", str(size))
        logger.info(f"悬浮球大小已更新为: {str(size)}")

    @staticmethod
    def set_ini_mini_image(image:str):
        """
        将 悬浮球背景写入到 INI 配置文件中，保留注释。
        :param image: str, 悬浮球背景图片。
        """
        config, ini_path = ConfigUtil.get_ini_config()
        # 更新配置值
        ConfigUtil.update_ini_line(ini_path, "Settings", "mini.image", image)
        return config.get("Settings", "mini.image", fallback=CommonUtil.get_mini_ico_full_path())

    @staticmethod
    def set_ini_tray_menu_checked(enabled):
        """
        将 托盘图标修改状态写入到 INI 配置文件中，保留注释。
        :param enabled: bool, True 表示启用 托盘图标修改，False 表示禁用。
        """
        config, ini_path = ConfigUtil.get_ini_config()
        # 更新配置值
        ConfigUtil.update_ini_line(ini_path, "Settings", "tray_menu.checked", "true" if enabled else "false")
        logger.info(f"托盘图标状态已更新为: {'启用' if enabled else '禁用'}")


    #
    @staticmethod
    def set_ini_tray_menu_image(image:str):
        """
        将 托盘图标写入到 INI 配置文件中，保留注释。
        :param image: str, 托盘图标图片。
        """
        config, ini_path = ConfigUtil.get_ini_config()
        # 更新配置值
        ConfigUtil.update_ini_line(ini_path, "Settings", "tray_menu.image", image)
        logger.info(f"托盘图标已更新为: {image}")

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
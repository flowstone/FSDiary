import os
import shutil
from src.const.fs_constants import FsConstants
from src.util.common_util import CommonUtil
from PySide6.QtGui import QFontDatabase, QPalette
from loguru import logger

from src.util.config_util import ConfigUtil


# 初始化文件
class AppInitUtil:

    # 初始化文件
    @staticmethod
    def write_init_file():

        external_dir = CommonUtil.get_external_path()
        # 创建基础文件夹
        if not os.path.exists(external_dir):
            logger.info(f"创建FSDiary文件夹:{external_dir}")
            os.makedirs(external_dir)

        # 复制app.ini文件
        source_file = CommonUtil.get_resource_path(FsConstants.APP_INI_FILE)
        destination_file = os.path.join(CommonUtil.get_external_path(), FsConstants.EXTERNAL_APP_INI_FILE)
        # 如果目标文件不存在，则复制
        if not os.path.exists(destination_file):
            logger.info(f"复制app.ini文件:{source_file} -> {destination_file}")
            shutil.copyfile(source_file, destination_file)

    @staticmethod
    def load_external_stylesheet(app):
        # 加载样式表文件
        stylesheet_path = CommonUtil.get_resource_path(FsConstants.BASE_QSS_PATH)
        if os.path.exists(stylesheet_path):
            with open(stylesheet_path, "r", encoding='utf-8') as file:
                stylesheet = file.read()
                # 为应用程序设置样式表
                app.setStyleSheet(stylesheet)

    # 加载外部字体
    @staticmethod
    def load_external_font():
        font_path = CommonUtil.get_resource_path(FsConstants.FONT_FILE_PATH)
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            logger.warning("字体加载失败")
        else:
            logger.info("字体加载成功")
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            return font_family


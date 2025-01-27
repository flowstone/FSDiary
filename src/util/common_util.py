import sys
import os
import datetime
import socket

from fs_base.base_util import BaseUtil
from loguru import logger
from src.const.fs_constants import FsConstants


class CommonUtil(BaseUtil):


    # 获得外部目录
    @staticmethod
    def get_external_path() -> str:
        # 使用内置配置路径
        # SAVE_FILE_PATH_WIN = "C:\\FSDiary\\"
        # SAVE_FILE_PATH_MAC = "~/FSDiary/"
        return FsConstants.SAVE_FILE_PATH_WIN if CommonUtil.check_win_os() else CommonUtil.get_mac_user_path()

    @staticmethod
    def get_diary_enc_path():
        data_path = CommonUtil.get_external_path()
        return os.path.join(data_path, FsConstants.DIARY_ENC_PATH)

    @staticmethod
    def get_diary_article_path():
        data_path = CommonUtil.get_external_path()
        return os.path.join(data_path, FsConstants.DIARY_ARTICLE_PATH)

    @staticmethod
    def get_diary_key_path():

        # 优先使用外部配置文件
        data_path = CommonUtil.get_external_path()
        return os.path.join(data_path, FsConstants.DIARY_KEY_PATH)
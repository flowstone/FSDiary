import sys
import os
import datetime
import socket

from loguru import logger
from src.const.fs_constants import FsConstants


class CommonUtil:

    # 获取资源（如图片等）的实际路径，处理打包后资源路径的问题
    @staticmethod
    def get_resource_path(relative_path):
        """
        获取资源（如图片等）的实际路径，处理打包后资源路径的问题
        """
        # PyInstaller、Nuitka打包单文件 写入的参数
        if "NUITKA_ONEFILE_PARENT" in os.environ or getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # 如果是冻结状态（例如使用 PyInstaller、Nuitka 等打包后的状态）
            # sys.executable 当前程序运行的目录，仅支持Win系统
            # sys._MEIPASS 是一个存储了程序资源的临时目录
            # 当程序被打包时，资源会被解压到该目录中
            # 此路径和打包的应用有关系，目前pyinstaller打macOS端，Nuitka打Win端
            if CommonUtil.check_win_os():
                application_path = os.path.dirname(sys.executable)
            else:
                application_path = sys._MEIPASS
            # logger.info("[冻结状态]打包后的资源路径:{}".format(application_path))
        else:
            # 如果不是冻结状态，使用当前脚本所在的目录
            #application_path = os.path.dirname(os.path.abspath(__file__))
            application_path = os.path.dirname(sys.argv[0])
            # logger.info("[非冻结状态]打包后的资源路径:{}".format(application_path))
        return os.path.join(application_path, relative_path)

    # 当前系统是Win 返回True
    @staticmethod
    def check_win_os():
        return sys.platform.startswith('win')

    # 当前系统是Mac 返回True
    @staticmethod
    def check_mac_os():
        return sys.platform.startswith("darwin")

    # 当前系统是Linux 返回True
    @staticmethod
    def check_linux_os():
        return sys.platform.startswith('linux')

    #获得应用图标全路径
    @staticmethod
    def get_ico_full_path():
        return CommonUtil.get_resource_path(FsConstants.APP_ICON_FULL_PATH)

    # 获得应用小图标全路径
    @staticmethod
    def get_mini_ico_full_path():
        return CommonUtil.get_resource_path(FsConstants.APP_MINI_ICON_FULL_PATH)



    # 静止外部类调用这个方法
    @staticmethod
    def get_mac_user_path():
        return os.path.expanduser(FsConstants.SAVE_FILE_PATH_MAC)

    # 获得当前日期
    @staticmethod
    def get_today():
        # 获取当前日期（是一个date对象）
        current_date = datetime.date.today()
        # 使用strftime方法按照指定格式进行格式化
        return current_date.strftime('%Y-%m-%d')

    # 获得当前指定格式的时间
    # %Y-%m-%d %H:%M:%S
    @staticmethod
    def get_current_time(format:str='%Y-%m-%d %H:%M:%S'):
        # 获取当前日期和时间
        current_datetime = datetime.datetime.now()

        # 格式化时间为指定格式
        return current_datetime.strftime(format)

    #递归函数来遍历文件夹及其子文件夹中的所有文件
    @staticmethod
    def count_files_in_directory_tree(folder_path:str):
        """
        递归函数来遍历文件夹及其子文件夹中的所有文件
        """
        count = 0
        for root, dirs, files in os.walk(folder_path):
            count += len(files)
        return count

    # 统计指定文件夹下文件的个数（不进入子文件夹统计）
    @staticmethod
    def count_files_in_current_folder(folder_path: str):
        """
        统计指定文件夹下文件的个数（不进入子文件夹统计）
        """
        file_count = 0
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path):
                file_count += 1
        return file_count

    # 统计文件夹下的所有文件夹总数
    @staticmethod
    def count_folders_in_current_folder(folder_path: str):
        """
        统计指定文件夹下的文件夹数量（不进入子文件夹统计）
        """
        folder_count = 0
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                folder_count += 1
        return folder_count




    @staticmethod
    def format_time(current_datetime):
        format: str = '%Y-%m-%d %H:%M:%S'
        # 将时间戳转换为datetime对象
        dt_object = datetime.datetime.fromtimestamp(current_datetime)
        # 格式化时间，这里使用了常见的年-月-日 时:分:秒格式
        # 格式化时间为指定格式
        return dt_object.strftime(format)

    # 本地IP
    @staticmethod
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # 使用公网 IP 测试本地地址
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            return "127.0.0.1"

    # 优先使用外部配置文件，如果外部配置文件不存在，则使用内部配置文件
    @staticmethod
    def get_app_ini_path():
        """
        获取应用程序配置文件的路径
        """
        # 优先使用外部配置文件
        data_path = CommonUtil.get_external_path()
        app_ini_path =  os.path.join(data_path, FsConstants.EXTERNAL_APP_INI_FILE)
        if os.path.exists(app_ini_path):
            # 如果外部配置文件存在，则使用外部配置文件
            #logger.info(f"使用外部配置文件:{app_ini_path}")
            return app_ini_path
        # 否则使用内部配置文件
        #logger.info(f"使用内部配置文件:{FsConstants.APP_INI_FILE}")
        return CommonUtil.get_resource_path(FsConstants.APP_INI_FILE)

    # 获得外部目录
    @staticmethod
    def get_external_path() -> str:
        # 使用内置配置路径
        # SAVE_FILE_PATH_WIN = "C:\\FSDiary\\"
        # SAVE_FILE_PATH_MAC = "~/FSDiary/"
        return FsConstants.SAVE_FILE_PATH_WIN if CommonUtil.check_win_os() else CommonUtil.get_mac_user_path()

    @staticmethod
    def get_diary_enc_path():

        # 优先使用外部配置文件
        data_path = CommonUtil.get_external_path()
        return os.path.join(data_path, FsConstants.DIARY_ROOT_PATH)

    @staticmethod
    def get_diary_key_path():

        # 优先使用外部配置文件
        data_path = CommonUtil.get_external_path()
        return os.path.join(data_path, FsConstants.DIARY_KEY_PATH)
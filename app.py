# macOS 打包
# nuitka-project-if: {OS} == "Darwin":
# 打包成.app程序时，是文件夹类型，只能使用 standalone
#    nuitka-project: --standalone
# macOS 必须参数
#    nuitka-project: --macos-create-app-bundle
#    nuitka-project: --macos-app-icon={MAIN_DIRECTORY}/resources/images/app.icns
# Windows 打包成单文件exe
# nuitka-project-if: {OS} == "Windows":
#    nuitka-project: --onefile
#    nuitka-project: --windows-icon-from-ico={MAIN_DIRECTORY}/resources/images/app.ico
# 特有配置  禁用命令窗口
#    nuitka-project: --windows-console-mode=disable

# 打包单文件的系统
# nuitka-project-if: {OS} in ("Linux", "FreeBSD", "OpenBSD"):
#    nuitka-project: --onefile

# 引入插件PySide6
# nuitka-project: --plugin-enable=pyside6
# 添加数据目录
# nuitka-project: --include-data-dir={MAIN_DIRECTORY}/resources=resources
# 添加数据文件
# nuitka-project: --include-data-files={MAIN_DIRECTORY}/app.ini=app.ini



import sys
from multiprocessing import freeze_support
import multiprocessing

from PySide6.QtGui import QFont, QPalette
from PySide6.QtWidgets import QApplication, QStyleFactory
from loguru import logger

from src.main_window import MainWindow
from src.util.app_init_util import AppInitUtil
from src.util.config_util import ConfigUtil
from src.util.common_util import CommonUtil
from src.const.fs_constants import FsConstants
import  os


# 配置 loguru 日志输出（可选）
logger.add(f"{CommonUtil.get_external_path()}/error.log", rotation="10 MB", retention="10 days", level="ERROR")

@logger.catch
def main():
    app = QApplication(sys.argv)


    # 初始化配置文件
    AppInitUtil.write_init_file()


    # 加载样式表文件
    AppInitUtil.load_external_stylesheet(app)


    # Qt界面风格
    #Windows 风格：标签会显示为按钮样式。
    #Macintosh 风格：标签看起来更加扁平，符合macOS的设计。
    #Fusion 风格：提供统一的现代外观，适合跨平台使用。
    app.setStyle(QStyleFactory.create("Fusion"))

    # 加载外部字体
    font_family = AppInitUtil.load_external_font()
    if font_family:
        app.setFont(QFont(font_family))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':

    main()

import sys

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTabWidget
)
from loguru import logger


from src.const.fs_constants import FsConstants
from src.option_general import OptionGeneral
from src.option_webdav_sync import OptionWebDavSync
from src.util.common_util import CommonUtil
from src.widget.tabwidget_animation import AnimatedTabWidget


class OptionTab(QWidget):

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        logger.info(f"---- 初始化{FsConstants.PREFERENCES_WINDOW_TITLE} ----")
        self.setWindowTitle(FsConstants.PREFERENCES_WINDOW_TITLE)
        self.setWindowIcon(QIcon(CommonUtil.get_ico_full_path()))
        self.setMinimumWidth(600)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setAcceptDrops(True)

        # 创建主布局
        layout = QVBoxLayout(self)
        # 创建 TabWidget
        self.tab_widget = AnimatedTabWidget()
        # 添加标签页
        self.add_tabs()
        # 将 TabWidget 添加到布局
        layout.addWidget(self.tab_widget)
        # 设置主窗口布局
        self.setLayout(layout)

    def add_tabs(self):
        self.tab_widget.addTab(OptionGeneral(), "基础")
        self.tab_widget.addTab(OptionWebDavSync(), "同步")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OptionTab()
    window.show()
    sys.exit(app.exec())
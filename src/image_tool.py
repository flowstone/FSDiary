import sys
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget, QToolBox
from loguru import logger

from src.batch_watermark import BatchWatermarkApp
from src.const.fs_constants import FsConstants
from src.image_compressor import ImageCompressor
from src.image_editor import ImageEditor
from src.image_resize import ImageResizeApp
from src.image_rotate import ImageRotateApp
from src.util.common_util import CommonUtil
from src.widget.tabwidget_animation import AnimatedTabWidget
from src.widget.toolbox_animation import AnimatedToolBox


class ImageToolApp(QWidget):
    """

    """
    closed_signal = Signal()  # 窗口关闭时发出的信号

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        logger.info(f"---- 初始化{FsConstants.WINDOW_TITLE_IMAGE_TOOL} ----")
        self.setWindowTitle(FsConstants.WINDOW_TITLE_IMAGE_TOOL)
        self.setWindowIcon(QIcon(CommonUtil.get_ico_full_path()))
        self.setFixedWidth(700)
        self.setFixedHeight(700)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setAcceptDrops(True)

        # 创建主布局
        layout = QVBoxLayout(self)

        # 创建 QToolBox
        self.toolbox = AnimatedToolBox()
        self.toolbox.setObjectName("mainToolBox")

        # 添加工具箱子项
        self.add_toolbox_items()

        # 将 ToolBox 添加到主布局
        layout.addWidget(self.toolbox)

        # 设置窗口布局
        self.setLayout(layout)


    def add_toolbox_items(self):
        """向 QToolBox 添加子项"""
        # 每个工具箱子项中都添加一个 QTabWidget
        toolbox_data = [
            ("图片", [
                (ImageCompressor(), "压缩"),
                (ImageRotateApp(), "旋转"),
                (ImageResizeApp(), "尺寸"),
                (ImageEditor(), "裁剪[废弃]"),
                # (RenameReplaceApp(), "替换"),
            ]),
            ("批量", [
                (BatchWatermarkApp(), "加水印"),
            ]),
            # ("高级", [
            #     (FileGeneratorApp(), "文件生成"),
            #     (FileComparatorApp(), "文件比较"),
            #     (FileEncryptorApp(), "文件加密(递归)"),
            # ]),
        ]

        for toolbox_title, tabs in toolbox_data:
            tab_widget = self.create_tab_widget(tabs)
            self.toolbox.addItem(tab_widget, toolbox_title)

    @staticmethod
    def create_tab_widget(tabs):
        """
        创建一个 QTabWidget 并为其添加标签页
        :param tabs: List[Tuple[QWidget, str]] 子页面和标题的列表
        :return: QTabWidget
        """
        tab_widget = AnimatedTabWidget()
        tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        tab_widget.setDocumentMode(True)

        for tab, title in tabs:
            tab_widget.addTab(tab, title)

        return tab_widget


    def closeEvent(self, event):
        """窗口关闭事件"""
        logger.info("窗口正在关闭...")
        self.closed_signal.emit()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageToolApp()
    window.show()
    sys.exit(app.exec())

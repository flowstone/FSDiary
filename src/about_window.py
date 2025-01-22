from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QScrollArea, QWidget, QFrame
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices

from src.const.fs_constants import FsConstants
from src.util.common_util import CommonUtil
from src.widget.menu_window_widget import MenuWindowWidget


class AboutWindow(MenuWindowWidget):
    def __init__(self):
        super().__init__()
        app_name = FsConstants.APP_WINDOW_TITLE
        copyright_info = FsConstants.COPYRIGHT_INFO
        version = FsConstants.VERSION
        license_file = CommonUtil.get_resource_path(FsConstants.LICENSE_FILE_PATH)
        icon_path = CommonUtil.get_ico_full_path()
        update_url = f"{FsConstants.PROJECT_ADDRESS}/releases"
        doc_url= FsConstants.PROJECT_ADDRESS
        self.setWindowTitle("关于")
        self.setFixedSize(600, 400)

        # 主布局
        layout = QVBoxLayout(self)

        # 应用图标
        if icon_path:
            icon_label = QLabel()
            pixmap = QPixmap(icon_path).scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(icon_label)

        # 标题和版本号布局
        title_version_layout = QHBoxLayout()

        # 应用名称（左对齐）
        name_label = QLabel(f"<h2>{app_name}</h2>")
        name_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title_version_layout.addWidget(name_label)

        # 版本号（右对齐）
        version_label = QLabel(f"<b>版本号：</b>{version}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        title_version_layout.addWidget(version_label)

        # 添加标题和版本号到主布局
        layout.addLayout(title_version_layout)

        # 版权信息（左对齐）
        copyright_label = QLabel(f"<a href='{FsConstants.PROJECT_ADDRESS}'>{copyright_info}</a>")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        copyright_label.setOpenExternalLinks(True)  # 支持点击超链接
        layout.addWidget(copyright_label)

        # 许可证文本滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # 许可证标题
        license_title = QLabel("<b>许可证条款：</b>")
        license_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        scroll_layout.addWidget(license_title)

        # 读取本地许可证内容
        try:
            with open(license_file, "r", encoding="utf-8") as file:
                license_text = file.read()
        except FileNotFoundError:
            license_text = "许可证文件未找到。"

        # 许可证内容
        license_label = QLabel(license_text)
        license_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        license_label.setWordWrap(True)  # 自动换行
        scroll_layout.addWidget(license_label)

        scroll_area.setWidget(scroll_content)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)  # 去掉边框
        layout.addWidget(scroll_area, stretch=1)

        # 联系
        contact_label = QLabel(f"联系：<a href='mailto:{FsConstants.AUTHOR_MAIL}'>{FsConstants.AUTHOR_MAIL}</a>")
        contact_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        contact_label.setOpenExternalLinks(True)  # 支持点击超链接
        layout.addWidget(contact_label)

        # 按钮布局
        button_layout = QHBoxLayout()

        # 检查更新按钮
        update_button = QPushButton("检查更新")
        update_button.setFixedWidth(120)
        update_button.setStyleSheet("padding: 8px; font-size: 14px;")
        update_button.clicked.connect(lambda: self.open_url(update_url))
        button_layout.addWidget(update_button)

        # 查看文档按钮
        doc_button = QPushButton("查看文档")
        doc_button.setFixedWidth(120)
        doc_button.setStyleSheet("padding: 8px; font-size: 14px;")
        doc_button.clicked.connect(lambda: self.open_url(doc_url))
        button_layout.addWidget(doc_button)

        layout.addLayout(button_layout)



        # 设置布局边距
        layout.setContentsMargins(20, 20, 20, 20)

    @staticmethod
    def open_url(url: str):
        """打开指定的 URL"""
        QDesktopServices.openUrl(QUrl(url))


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    dialog = AboutWindow()
    dialog.show()
    sys.exit(app.exec())

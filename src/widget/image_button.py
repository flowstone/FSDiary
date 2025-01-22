
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QPixmap, QIcon
from src.util.common_util import CommonUtil

# 图片按钮
class ImageButton(QPushButton):
    def __init__(self, normal_image_path, parent=None):
        super().__init__(parent)

        self.normal_pixmap = QPixmap(CommonUtil.get_resource_path(normal_image_path))

        self.setIcon(QIcon(self.normal_pixmap))
        # 设置按钮的固定大小为正常状态图片的尺寸（可根据实际需求考虑是否以点击后图片尺寸为准等）
        self.setFixedSize(30, 30)
        # 避免外部QSS影响
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                min-width: 0px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;  /* 悬停时背景色 */
            }
            QPushButton:pressed {
                background-color: #b0b0b0;  /* 按下时背景色 */
            }
        """)


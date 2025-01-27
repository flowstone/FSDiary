from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QPixmap, QIcon
from src.util.common_util import CommonUtil


# 图片按钮
class HoverImageButton(QPushButton):
    def __init__(self, normal_image_path, hover_image_path, parent=None):
        super().__init__(parent)

        self.normal_pixmap = QPixmap(CommonUtil.get_resource_path(normal_image_path))
        self.clicked_pixmap = QPixmap(CommonUtil.get_resource_path(hover_image_path))

        self.setIcon(QIcon(self.normal_pixmap))
        # 设置按钮的固定大小为正常状态图片的尺寸（可根据实际需求考虑是否以点击后图片尺寸为准等）
        self.setFixedSize(30, 30)
        # 避免外部QSS影响
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                min-width: 0px;
            }
        """)
        self.clicked.connect(self.toggle_image)  # 连接点击信号到切换图片的方法

    def toggle_image(self):
        """
        使用状态变量控制图片切换，可灵活设置切换逻辑
        """
        # 获取状态变量，若不存在则初始化为False
        self.is_clicked_image_showed = getattr(self, 'is_clicked_image_showed', False)
        if self.is_clicked_image_showed:
            self.setIcon(QIcon(self.normal_pixmap))
            self.is_clicked_image_showed = False
        else:
            self.setIcon(QIcon(self.clicked_pixmap))
            self.is_clicked_image_showed = True
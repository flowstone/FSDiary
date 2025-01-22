from PySide6.QtGui import QPainter, QPen, QColor, Qt
from PySide6.QtWidgets import QLabel

class ImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selection_rect = None  # 裁剪区域
        self.is_cropping = False  # 是否正在裁剪

    def paintEvent(self, event):
        """重绘事件，用于绘制裁剪矩形"""
        super().paintEvent(event)  # 调用父类的绘制逻辑

        if self.is_cropping and self.selection_rect:
            painter = QPainter(self)
            painter.setPen(QPen(QColor(255, 0, 0, 150), 2, Qt.PenStyle.DashLine))  # 半透明红色虚线
            painter.drawRect(self.selection_rect)  # 绘制裁剪区域
            painter.end()

from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QApplication, QMainWindow, QToolBox, QLabel, QVBoxLayout, QWidget


class AnimatedToolBox(QToolBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation = None
        self.previous_index = -1

        # 监听当前索引的变化
        self.currentChanged.connect(self.animate_expansion)

    def animate_expansion(self, index):
        """实现展开/折叠动画"""
        # 如果有之前的动画，先停止
        if self.animation:
            self.animation.stop()

        # 获取当前页面的高度
        current_widget = self.widget(index)
        target_height = current_widget.sizeHint().height()

        # 如果之前有展开的页面，则折叠其高度为 0
        if self.previous_index != -1 and self.previous_index != index:
            previous_widget = self.widget(self.previous_index)
            self._animate_widget_height(previous_widget, previous_widget.height(), 0)

        # 展开当前页面
        self._animate_widget_height(current_widget, 0, target_height)

        # 更新之前的索引
        self.previous_index = index

    def _animate_widget_height(self, widget, start_height, end_height):
        """对单个页面高度进行动画处理"""
        self.animation = QPropertyAnimation(widget, b"maximumHeight")
        self.animation.setDuration(300)  # 动画时长（毫秒）
        self.animation.setStartValue(start_height)
        self.animation.setEndValue(end_height)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)  # 动画曲线
        self.animation.start()

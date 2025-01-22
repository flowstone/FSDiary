from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QLabel,
    QStackedWidget, QSizePolicy,
)


class AnimatedTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabPosition(QTabWidget.TabPosition.North)  # 设置标签位置
        #self.currentChanged.connect(self.animate_tab_switch)
        #self.animation = QPropertyAnimation()

    def animate_tab_switch(self, index):
        """实现标签切换动画"""
        # 获取 QStackedWidget 的当前和目标页面
        current_widget = self.currentWidget()
        target_widget = self.widget(index)

        # 初始化动画属性
        self.animation.stop()
        self.animation = QPropertyAnimation(self.currentWidget(), b"geometry")
        self.animation.setDuration(300)  # 动画持续时间（毫秒）
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)  # 动画曲线

        # 获取当前和目标页面的几何位置
        start_geometry = current_widget.geometry()
        end_geometry = target_widget.geometry()

        # 设置起点和终点
        self.animation.setStartValue(start_geometry)
        self.animation.setEndValue(end_geometry)

        # 启动动画
        self.animation.start()
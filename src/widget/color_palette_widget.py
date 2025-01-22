from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QColorDialog, QLabel
from PySide6.QtGui import QColor
from PySide6.QtCore import Signal


class ColorPaletteWidget(QWidget):
    """
    调色板组件，支持颜色管理和颜色选择
    """
    color_added = Signal(QColor)  # 当新颜色被添加时触发信号
    color_selected = Signal(QColor)  # 当颜色被选择时触发信号

    def __init__(self, initial_colors=None):
        super().__init__()
        self.setWindowTitle("调色板")
        self.setMinimumSize(300, 200)

        # 初始化颜色列表
        self.colors = initial_colors if initial_colors else [
            QColor("#FF5733"),  # 红色
            QColor("#33FF57"),  # 绿色
            QColor("#3357FF"),  # 蓝色
            QColor("#FFD700"),  # 金色
            QColor("#FF33A6"),  # 粉色
        ]

        # 布局
        self.layout = QVBoxLayout(self)

        # 显示颜色的区域
        self.color_display_layout = QHBoxLayout()
        self.layout.addLayout(self.color_display_layout)

        # 添加颜色按钮
        self.add_color_button = QPushButton("添加颜色")
        self.add_color_button.clicked.connect(self.open_color_dialog)
        self.layout.addWidget(self.add_color_button)

        # 初始化颜色显示
        self.update_color_display()

    def open_color_dialog(self):
        """打开颜色选择对话框以添加新颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.colors.append(color)
            self.color_added.emit(color)
            self.update_color_display()

    def update_color_display(self):
        """刷新颜色显示区域"""
        # 清空现有的颜色显示
        for i in reversed(range(self.color_display_layout.count())):
            widget = self.color_display_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # 重新创建颜色显示
        for color in self.colors:
            color_button = QPushButton()
            color_button.setFixedSize(30, 30)
            color_button.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
            color_button.clicked.connect(lambda _, c=color: self.color_selected.emit(c))
            self.color_display_layout.addWidget(color_button)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("调色板示例")
            self.setGeometry(100, 100, 400, 300)

            # 初始化调色板组件
            self.palette_widget = ColorPaletteWidget()
            self.setCentralWidget(self.palette_widget)

            # 连接信号
            self.palette_widget.color_added.connect(self.on_color_added)
            self.palette_widget.color_selected.connect(self.on_color_selected)

        def on_color_added(self, color: QColor):
            print(f"添加了新颜色: {color.name()}")

        def on_color_selected(self, color: QColor):
            print(f"选择了颜色: {color.name()}")

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

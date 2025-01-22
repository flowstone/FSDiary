from PySide6.QtWidgets import QApplication, QWidget, QToolBar, QVBoxLayout, QStatusBar, QLabel, QMainWindow
from PySide6.QtGui import QIcon, QColor, QAction
from PySide6.QtCore import Qt


class CustomToolbar(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("自定义工具栏")
        self.setMinimumSize(600, 400)

        # 初始化状态栏和工具栏
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        # 状态显示区域
        self.tool_status_label = QLabel("当前工具：无", self)
        self.tool_status_label.setStyleSheet("font-size: 14px; color: black;")
        self.status_bar.addWidget(self.tool_status_label)

        # 创建工具栏
        self.toolbar = QToolBar(self)
        self.addToolBar(self.toolbar)

        # 添加工具按钮
        self.add_tool_action("撤销", "撤销", "undo.png", self.on_undo)
        self.add_tool_action("保存", "保存", "save.png", self.on_save)
        self.add_tool_action("选择工具", "选择工具", "select_tool.png", self.on_select_tool)

        # 添加颜色选择按钮
        self.color_action = QAction("选择颜色", self)
        self.color_action.setIcon(QIcon("color_picker.png"))
        self.color_action.setToolTip("选择颜色")
        self.color_action.triggered.connect(self.on_choose_color)
        self.toolbar.addAction(self.color_action)

    def add_tool_action(self, label, tooltip, icon_path, callback):
        """动态添加工具按钮"""
        action = QAction(QIcon(icon_path), label, self)
        action.setToolTip(tooltip)
        action.triggered.connect(callback)
        self.toolbar.addAction(action)

    def on_undo(self):
        """撤销操作"""
        self.tool_status_label.setText("当前工具：撤销")

    def on_save(self):
        """保存操作"""
        self.tool_status_label.setText("当前工具：保存")

    def on_select_tool(self):
        """选择工具操作"""
        self.tool_status_label.setText("当前工具：选择工具")

    def on_choose_color(self):
        """颜色选择操作"""
        color = QColor(255, 0, 0)  # 红色作为示例
        self.tool_status_label.setText(f"当前颜色：{color.name()}")


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    window = CustomToolbar()
    window.show()

    sys.exit(app.exec())

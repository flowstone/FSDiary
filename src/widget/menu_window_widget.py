from PySide6.QtWidgets import QWidget


class MenuWindowWidget(QWidget):

    def __init__(self):
        super().__init__()

    #重写关闭事件
    def closeEvent(self, event):
        self.hide()  # 隐藏窗口而不是销毁
        event.ignore()  # 忽略关闭事件
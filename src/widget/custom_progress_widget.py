from PySide6.QtWidgets import QProgressBar
from PySide6.QtCore import Qt


class CustomProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setValue(0)
        self.setMinimum(0)
        self.setMaximum(100)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            QProgressBar {
                text-align: center;
                font-size: 14px;
                color: black;
                font-weight: bold;
                height: 30px;
            }
            QProgressBar::chunk {
                border-radius: 5px;
                border: 2px solid transparent;  /* 边框设置为透明 */
                background-color: #00cc66;
                width: 10px;
            }
        """)

    def reset_progress(self):
        """
        重置进度条为初始状态
        """
        self.setValue(0)
    def set_range(self, min_value, max_value):
        """设置进度条的范围"""
        self.setRange(min_value, max_value)

    def update_progress(self, value):
        """
        更新进度条值
        :param value: 整数，进度值 (0-100)
        """
        self.setValue(value)
        if value < 50:
            self.setStyleSheet("""
                QProgressBar {
                    text-align: center;
                    font-size: 14px;
                    color: black;
                    font-weight: bold;
                    height: 30px;
                }
                QProgressBar::chunk {
                    border-radius: 5px;
                    border: 2px solid transparent;  /* 边框设置为透明 */
                    background-color: #ff6666;  /* 红色 */
                }
            """)
        elif value < 80:
            self.setStyleSheet("""
                QProgressBar {
                    text-align: center;
                    font-size: 14px;
                    color: black;
                    font-weight: bold;
                    height: 30px;
                }
                QProgressBar::chunk {
                    border-radius: 5px;
                    border: 2px solid transparent;  /* 边框设置为透明 */
                    background-color: #ffcc00;  /* 黄色 */
                }
            """)
        else:
            self.setStyleSheet("""
                QProgressBar {
                    text-align: center;
                    font-size: 14px;
                    color: black;
                    font-weight: bold;
                    height: 30px;
                }
                QProgressBar::chunk {
                    border-radius: 5px;
                    border: 2px solid transparent;  /* 边框设置为透明 */
                    background-color: #00cc66;  /* 绿色 */
                }
            """)
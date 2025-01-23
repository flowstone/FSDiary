from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QSplitter, QAbstractItemView
from PySide6.QtCore import Qt
from src.widget.markdown_editor import MarkdownEditor


class UiComponents(QWidget):
    def __init__(self):
        super().__init__()

        # 添加分割器
        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)

        # 左侧布局（按钮 + 列表）
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # 新建日记按钮
        self.add_button = QPushButton("新建日记")
        left_layout.addWidget(self.add_button)

        # 左侧列表
        self.diary_list = QListWidget()
        self.diary_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        left_layout.addWidget(self.diary_list)

        # 将左侧布局添加到分割器
        self.splitter.addWidget(left_widget)

        # 右侧编辑框
        self.diary_content = MarkdownEditor()
        #self.diary_content.textChanged.connect(start_save_timer_callback)  # 监听文本修改
        self.splitter.addWidget(self.diary_content)

        # 设置分割器的比例
        self.splitter.setStretchFactor(0, 2)  # 左侧占比较小
        self.splitter.setStretchFactor(1, 5)  # 右侧占比较大

        layout = QVBoxLayout(self)
        layout.addWidget(self.splitter)
        self.setLayout(layout)

        self.diary_list.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
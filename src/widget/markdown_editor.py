from PySide6 import QtCore
from markdown import markdown
from PySide6.QtWidgets import QPlainTextEdit, QTextBrowser, QVBoxLayout, QPushButton, QWidget, QHBoxLayout
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, Signal

from src.const.fs_constants import FsConstants
from src.util.common_util import CommonUtil
from src.widget.image_button import ImageButton


class MarkdownEditor(QWidget):
    # 定义一个自定义信号
    textChanged = Signal()
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout()

        button_layout = QHBoxLayout()

        # 切换按钮（图片按钮）
        self.preview_button = ImageButton(FsConstants.MARKDOWN_BTN_PATH)
        self.preview_button.clicked.connect(self.switch_to_preview)

        self.edit_button = ImageButton(FsConstants.EDIT_BTN_PATH)
        self.edit_button.clicked.connect(self.switch_to_edit)

        # 右对齐按钮
        # 直接将按钮添加到布局，并右对齐
        button_layout.setSpacing(2)  # 设置布局中的间隔为0
        # 直接将按钮添加到布局，并右对齐
        button_layout.addWidget(self.preview_button)
        button_layout.addWidget(self.edit_button)

        # 设置按钮布局靠右
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addLayout(button_layout)

        # 编辑框
        self.diary_editor = QPlainTextEdit(self)
        self.diary_editor.setPlaceholderText("在这里编写您的 Markdown 日记...")
        self.diary_editor.textChanged.connect(self.emit_text_changed)  # 绑定内部编辑框的信号
        main_layout.addWidget(self.diary_editor)

        # 预览框
        self.preview = QTextBrowser(self)
        self.preview.setVisible(False)  # 默认隐藏预览区域
        main_layout.addWidget(self.preview)

        self.setLayout(main_layout)

    def emit_text_changed(self):
        """当编辑器内容发生变化时触发自定义信号"""
        self.textChanged.emit()

    def switch_to_preview(self):
        """切换到预览模式"""
        self.preview.setVisible(True)
        self.diary_editor.setVisible(False)
        self.update_preview()

    def switch_to_edit(self):
        """切换到编辑模式"""
        self.preview.setVisible(False)
        self.diary_editor.setVisible(True)

    def update_preview(self):
        """实时更新 Markdown 预览"""
        content = self.diary_editor.toPlainText()

        # 使用 markdown 渲染为 HTML
        html_content = markdown(content)

        # 添加样式
        # 添加 Prism.js 样式和脚本
        styled_html = f"""
            <html>
            <head>
                <link href="https://cdn.jsdelivr.net/npm/prismjs@1.28.0/themes/prism-tomorrow.css" rel="stylesheet">
                <script src="https://cdn.jsdelivr.net/npm/prismjs@1.28.0/prism.js"></script>
                <script src="https://cdn.jsdelivr.net/npm/prismjs@1.28.0/components/prism-python.min.js"></script>  <!-- 例如添加Python高亮 -->
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 10px; }}
                    pre {{ background: #f4f4f4; padding: 10px; overflow: auto; }}
                    code {{ color: inherit; }}  <!-- 改为继承颜色 -->
                </style>
            </head>
            <body>
                {html_content}
            </body>
            <script>
                // 强制重新渲染代码块的高亮
                Prism.highlightAll();
            </script>
            </html>
            """
        self.preview.setHtml(styled_html)

    def get_content(self):
        """获取编辑器中的内容"""
        return self.diary_editor.toPlainText()

    def set_content(self, content):
        """设置编辑器中的内容"""
        self.diary_editor.setPlainText(content)

    def clear_content(self):
        self.diary_editor.clear()


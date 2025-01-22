from PySide6 import QtCore
from PySide6.QtWidgets import QPlainTextEdit, QTextBrowser, QVBoxLayout, QWidget, QSizePolicy
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Signal

from src.const.fs_constants import FsConstants
from src.util.common_util import CommonUtil
from src.widget.image_button import ImageButton
from markdown_it import MarkdownIt


from PySide6.QtWidgets import QToolBar

class MarkdownEditor(QWidget):
    # 定义一个自定义信号
    textChanged = Signal()

    def __init__(self):
        super().__init__()

        # 创建一个垂直布局
        main_layout = QVBoxLayout(self)

        # 添加工具栏
        self.add_toolbar()

        # 编辑框
        self.diary_editor = QPlainTextEdit(self)
        self.diary_editor.setPlaceholderText("在这里编写您的 Markdown 日记...")
        self.diary_editor.textChanged.connect(self.emit_text_changed)
        main_layout.addWidget(self.diary_editor)

        # 预览框
        self.preview = QTextBrowser(self)
        self.preview.setVisible(False)
        main_layout.addWidget(self.preview)

        # 设置主布局
        self.setLayout(main_layout)

    def add_toolbar(self):
        """添加工具栏"""
        toolbar = QToolBar("工具栏", self)

        # 设置工具栏图标大小
        toolbar.setIconSize(QtCore.QSize(24, 24))  # 设置图标大小为 24x24（可根据需要调整）

        # 加粗按钮
        bold_action = QAction(QIcon(CommonUtil.get_resource_path(FsConstants.BOLD_ICON_PATH)), "加粗", self)
        bold_action.triggered.connect(self.insert_bold)
        toolbar.addAction(bold_action)

        # 斜体按钮
        italic_action = QAction(QIcon(CommonUtil.get_resource_path(FsConstants.ITALIC_ICON_PATH)), "斜体", self)
        italic_action.triggered.connect(self.insert_italic)
        toolbar.addAction(italic_action)

        # 插入链接按钮
        link_action = QAction(QIcon(CommonUtil.get_resource_path(FsConstants.LINK_ICON_PATH)), "插入链接", self)
        link_action.triggered.connect(self.insert_link)
        toolbar.addAction(link_action)

        # 插入图片按钮
        image_action = QAction(QIcon(CommonUtil.get_resource_path(FsConstants.IMAGE_ICON_PATH)), "插入图片", self)
        image_action.triggered.connect(self.insert_image)
        toolbar.addAction(image_action)

        # 添加一个伸缩空间（spacer）将后续按钮推到右侧
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        # 添加切换到预览模式按钮
        preview_action = QAction(QIcon(CommonUtil.get_resource_path(FsConstants.MARKDOWN_BTN_PATH)), "插入图片", self)
        preview_action.triggered.connect(self.switch_to_preview)
        toolbar.addAction(preview_action)

        # 添加切换到编辑模式按钮
        edit_action = QAction(QIcon(CommonUtil.get_resource_path(FsConstants.EDIT_BTN_PATH)), "插入图片", self)
        edit_action.triggered.connect(self.switch_to_edit)
        toolbar.addAction(edit_action)


        # 将工具栏添加到布局中
        self.layout().addWidget(toolbar)

    def insert_bold(self):
        """插入加粗Markdown语法"""
        cursor = self.diary_editor.textCursor()
        cursor.insertText("**加粗文本**")
        self.diary_editor.setTextCursor(cursor)

    def insert_italic(self):
        """插入斜体Markdown语法"""
        cursor = self.diary_editor.textCursor()
        cursor.insertText("*斜体文本*")
        self.diary_editor.setTextCursor(cursor)

    def insert_link(self):
        """插入链接Markdown语法"""
        cursor = self.diary_editor.textCursor()
        cursor.insertText("[链接文字](http://example.com)")
        self.diary_editor.setTextCursor(cursor)

    def insert_image(self):
        """插入图片Markdown语法"""
        cursor = self.diary_editor.textCursor()
        cursor.insertText("![图片描述](http://example.com/image.jpg)")
        self.diary_editor.setTextCursor(cursor)

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

        # 使用 markdown-it-py 进行 Markdown 渲染
        md = MarkdownIt()
        html_content = md.render(content)

        # 添加样式
        styled_html = f"""
            <html>
            <head>
                <link href="https://cdn.jsdelivr.net/npm/prismjs@1.28.0/themes/prism-tomorrow.css" rel="stylesheet">
                <script src="https://cdn.jsdelivr.net/npm/prismjs@1.28.0/prism.js"></script>
                <script src="https://cdn.jsdelivr.net/npm/prismjs@1.28.0/components/prism-python.min.js"></script>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 10px; }}
                    pre {{ background: #f4f4f4; padding: 10px; overflow: auto; }}
                    code {{ color: inherit; }}
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
        self.preview.setOpenExternalLinks(True)  # 允许加载外部链接

    def get_content(self):
        """获取编辑器中的内容"""
        return self.diary_editor.toPlainText()

    def set_content(self, content):
        """设置编辑器中的内容"""
        self.diary_editor.setPlainText(content)

    def clear_content(self):
        self.diary_editor.clear()

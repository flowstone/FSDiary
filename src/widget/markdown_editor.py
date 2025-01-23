import os

from PySide6 import QtCore
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QPlainTextEdit, QTextBrowser, QVBoxLayout, QWidget, QSizePolicy, QColorDialog, \
    QInputDialog
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Signal, QUrl
from PySide6.QtWidgets import QInputDialog

from src.const.fs_constants import FsConstants
from src.util.app_init_util import AppInitUtil
from src.util.common_util import CommonUtil
from src.widget.image_button import ImageButton
from markdown_it import MarkdownIt
from datetime import datetime  # 用于插入时间
from loguru import  logger
from PySide6.QtWidgets import QToolBar

#os.environ["FC_DEBUG"] = "1"  # 打开字体调试模式

class MarkdownEditor(QWidget):
    # 定义一个自定义信号
    textChanged = Signal()

    def __init__(self):
        super().__init__()
        self._is_preview = False

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
        self.preview = QWebEngineView(self)
        #self.preview.setUrl(QUrl("about:blank"))  # 设置初始空白页面
        self.preview.setVisible(False)

        main_layout.addWidget(self.preview)

        # 设置主布局
        self.setLayout(main_layout)

    def add_toolbar(self):
        """添加工具栏"""
        toolbar = QToolBar("工具栏", self)

        # 设置工具栏图标大小
        toolbar.setIconSize(QtCore.QSize(24, 24))  # 设置图标大小为 24x24（可根据需要调整）

        # 按钮引用字典，用于统一管理
        self.toolbar_actions = {}
        # 加粗按钮
        bold_action = QAction(QIcon(CommonUtil.get_resource_path(FsConstants.BOLD_ICON_PATH)), "加粗", self)
        bold_action.triggered.connect(self.insert_bold)
        toolbar.addAction(bold_action)
        self.toolbar_actions['bold'] = bold_action

        # 斜体按钮
        italic_action = QAction(QIcon(CommonUtil.get_resource_path(FsConstants.ITALIC_ICON_PATH)), "斜体", self)
        italic_action.triggered.connect(self.insert_italic)
        toolbar.addAction(italic_action)
        self.toolbar_actions['italic'] = italic_action

        # 插入链接按钮
        link_action = QAction(QIcon(CommonUtil.get_resource_path(FsConstants.LINK_ICON_PATH)), "插入链接", self)
        link_action.triggered.connect(self.insert_link)
        toolbar.addAction(link_action)
        self.toolbar_actions['link'] = link_action

        # 插入图片按钮
        image_action = QAction(QIcon(CommonUtil.get_resource_path(FsConstants.IMAGE_ICON_PATH)), "插入图片", self)
        image_action.triggered.connect(self.insert_image)
        toolbar.addAction(image_action)
        self.toolbar_actions['image'] = image_action


        # 添加文字颜色按钮
        color_action = QAction(QIcon(CommonUtil.get_resource_path(FsConstants.COLOR_ICON_PATH)), "插入颜色", self)
        color_action.triggered.connect(self.insert_color)
        toolbar.addAction(color_action)
        self.toolbar_actions['color'] = color_action

        # 插入水平线按钮
        hr_action = QAction(QIcon(CommonUtil.get_resource_path(FsConstants.HR_ICON_PATH)), "插入水平线", self)
        hr_action.triggered.connect(self.insert_horizontal_line)
        toolbar.addAction(hr_action)
        self.toolbar_actions['hr'] = hr_action

        # 插入引用块按钮
        blockquote_action = QAction(QIcon(CommonUtil.get_resource_path(FsConstants.BLOCKQUOTE_ICON_PATH)), "插入引用块", self)
        blockquote_action.triggered.connect(self.insert_blockquote)
        toolbar.addAction(blockquote_action)
        self.toolbar_actions['blockquote'] = blockquote_action

        # 动态表格按钮
        dynamic_table_action = QAction(QIcon(CommonUtil.get_resource_path(FsConstants.TABLE_ICON_PATH)), "插入表格", self)
        dynamic_table_action.triggered.connect(self.insert_dynamic_table)
        toolbar.addAction(dynamic_table_action)
        self.toolbar_actions['table'] = dynamic_table_action

        # 插入时间戳按钮
        timestamp_action = QAction(QIcon(CommonUtil.get_resource_path(FsConstants.TIMESTAMP_ICON_PATH)), "插入时间", self)
        timestamp_action.triggered.connect(self.insert_time)
        toolbar.addAction(timestamp_action)
        self.toolbar_actions['timestamp'] = timestamp_action

        # 添加一个伸缩空间（spacer）将后续按钮推到右侧
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        # 添加切换到预览模式按钮
        preview_action = QAction(QIcon(CommonUtil.get_resource_path(FsConstants.MARKDOWN_BTN_PATH)), "预览模式", self)
        preview_action.triggered.connect(self.switch_to_preview)
        toolbar.addAction(preview_action)
        self.toolbar_actions['preview'] = preview_action

        # 添加切换到编辑模式按钮
        edit_action = QAction(QIcon(CommonUtil.get_resource_path(FsConstants.EDIT_BTN_PATH)), "编辑模式", self)
        edit_action.triggered.connect(self.switch_to_edit)
        toolbar.addAction(edit_action)
        self.toolbar_actions['edit'] = edit_action


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

    def insert_color(self):
        """插入带有用户选择颜色的文字"""
        # 打开颜色选择器
        color = QColorDialog.getColor()

        # 如果用户选择了有效的颜色
        if color.isValid():
            color_code = color.name()  # 获取颜色的十六进制代码
            cursor = self.diary_editor.textCursor()
            cursor.insertText(f'<span style="color: {color_code};">自定义颜色文字</span>')
            self.diary_editor.setTextCursor(cursor)


    def insert_horizontal_line(self):
        """插入水平线"""
        cursor = self.diary_editor.textCursor()
        cursor.insertText("\n---\n")
        self.diary_editor.setTextCursor(cursor)

    def insert_blockquote(self):
        """插入引用"""
        cursor = self.diary_editor.textCursor()
        cursor.insertText("> 引用文本")
        self.diary_editor.setTextCursor(cursor)


    def insert_dynamic_table(self):
        """通过用户输入动态生成表格"""
        # 获取用户输入的行数和列数
        rows, ok_rows = QInputDialog.getInt(self, "输入表格行数", "行数：", minValue=1, maxValue=20)
        if not ok_rows:
            return

        cols, ok_cols = QInputDialog.getInt(self, "输入表格列数", "列数：", minValue=1, maxValue=20)
        if not ok_cols:
            return

        # 动态生成表格模板
        header = "| " + " | ".join([f"Header {i + 1}" for i in range(cols)]) + " |\n"
        separator = "| " + " | ".join(["-" * 8 for _ in range(cols)]) + " |\n"
        rows_data = "".join(["| " + " | ".join([f"Cell {i + 1}" for i in range(cols)]) + " |\n" for _ in range(rows)])

        table_template = header + separator + rows_data

        # 插入表格到文本编辑器
        cursor = self.diary_editor.textCursor()
        cursor.insertText(table_template)
        self.diary_editor.setTextCursor(cursor)

    def insert_time(self):
        """插入当前时间"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor = self.diary_editor.textCursor()
        cursor.insertText(current_time)
        self.diary_editor.setTextCursor(cursor)

    def emit_text_changed(self):
        """当编辑器内容发生变化时触发自定义信号"""
        self.textChanged.emit()

    def is_preview_mode(self):
        """检查是否处于预览模式"""
        return self._is_preview



    def switch_to_preview(self):
        """切换到预览模式"""
        self.diary_editor.setVisible(False)
        self.preview.setVisible(True)
        self._is_preview = True
        self.update_preview()
        # 禁用所有工具栏按钮，除了“编辑模式”按钮
        for action_name, action in self.toolbar_actions.items():
            if action_name != 'edit':
                action.setDisabled(True)

    def switch_to_edit(self):
        """切换到编辑模式"""
        self.preview.setVisible(False)
        self.diary_editor.setVisible(True)
        self._is_preview = False
        # 启用所有工具栏按钮
        for action in self.toolbar_actions.values():
            action.setDisabled(False)

    def update_preview(self):
        """实时更新 Markdown 预览"""
        content = self.diary_editor.toPlainText()

        # 使用 markdown-it-py 进行 Markdown 渲染
        # 启用表格解析功能
        md = MarkdownIt("commonmark").enable("table")
        html_content = md.render(content)
        # 添加样式
        styled_html = f"""
            <html>
            <head>
                <meta charset="UTF-8">
                <link href="https://cdn.jsdelivr.net/npm/prismjs@1.28.0/themes/prism-tomorrow.css" rel="stylesheet">
                <script src="https://cdn.jsdelivr.net/npm/prismjs@1.28.0/prism.js"></script>
                <script src="https://cdn.jsdelivr.net/npm/prismjs@1.28.0/components/prism-python.min.js"></script>
                <style>
                    body {{ 
                        font-family: "Consolas","Courier New",sans-serif;
                        background-color: #f5f5f5; 
                        border: 1px solid #dcdcdc; 
                        font-size: 14px; 
                        border-radius: 8px; 
                        line-height: 1.6; padding: 10px; }}
                    pre {{ padding: 10px; overflow: auto; }}
                    code {{ color: inherit; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            <script>
                  document.addEventListener("DOMContentLoaded", function () {{
                        if (typeof Prism === 'undefined') {{
                            console.error('Prism.js 未正确加载！');
                        }} else {{
                            console.log('Prism.js 加载成功');
                            Prism.highlightAll();

                        }}
                    }});
            </script>
            </html>
        """
        self.preview.setHtml(styled_html)

    def get_content(self):
        """获取编辑器中的内容"""
        return self.diary_editor.toPlainText()

    def set_content(self, content):
        """设置编辑器中的内容"""
        # 清空之前预览框中的值
        self.preview.setHtml("")
        self.diary_editor.setPlainText(content)

    def clear_content(self):
        self.diary_editor.clear()

    def get_preview_html(self, callback):
        """异步获取预览内容的HTML"""
        if self.is_preview_mode():
            self.preview.page().toHtml(callback)
        else:
            callback("")  # 编辑模式下没有预览内容
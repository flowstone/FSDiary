from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QListWidget, \
    QMessageBox, QInputDialog, QWidget, QMenu, QSplitter, QFileDialog, QAbstractItemView
from PySide6.QtCore import Qt, QTimer
import os
from loguru import logger

from src.const.fs_constants import FsConstants
from src.util.common_util import CommonUtil
from src.util.encryption_util import EncryptionUtil
from src.util.message_util import MessageUtil
from src.widget.markdown_editor import MarkdownEditor
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

DIARY_DIR = f"{CommonUtil.get_diary_enc_path()}"

class DiaryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("日记应用")

        # 加载加密密钥
        self.key = self.load_key()
        if not self.key:
            MessageUtil.show_error_message("无法加载密钥文件！")
            exit()

        # 当前日记文件
        self.current_file = None

        # 保存延迟计时器
        self.save_timer = QTimer()
        self.save_timer.setInterval(2000)  # 2 秒延迟
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.auto_save)

        self.init_ui()

    def init_ui(self):
        # 主界面布局
        main_layout = QHBoxLayout()
        # 添加分割器
        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        # 左侧布局（按钮 + 列表）
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # 新建日记按钮
        add_button = QPushButton("新建日记")
        add_button.clicked.connect(self.new_diary)
        left_layout.addWidget(add_button)

        # 左侧列表
        self.diary_list = QListWidget()
        self.diary_list.itemClicked.connect(self.load_diary)
        self.diary_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.diary_list.customContextMenuRequested.connect(self.show_context_menu)
        left_layout.addWidget(self.diary_list)

        # 将左侧布局添加到分割器
        self.splitter.addWidget(left_widget)

        # 右侧编辑框
        self.diary_content = MarkdownEditor()
        self.diary_content.textChanged.connect(self.start_save_timer)  # 监听文本修改
        self.splitter.addWidget(self.diary_content)

        # 设置分割器的比例
        self.splitter.setStretchFactor(0, 2)  # 左侧占比较小
        self.splitter.setStretchFactor(1, 5)  # 右侧占比较大

        # 添加分割器到主布局
        main_layout.addWidget(self.splitter)

        self.setLayout(main_layout)

        self.load_diary_list()

        self.diary_list.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

    def show_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu()

        # 添加删除选项
        delete_action = QAction("删除日记", self)
        delete_action.triggered.connect(self.delete_diary)
        menu.addAction(delete_action)

        # 重命名选项
        rename_action = QAction("重命名日记", self)
        rename_action.triggered.connect(self.rename_diary)
        menu.addAction(rename_action)

        # 重命名选项
        export_pdf_action = QAction("导出成PDF", self)
        export_pdf_action.triggered.connect(self.export_to_pdf)
        menu.addAction(export_pdf_action)

        # 在列表中显示右键菜单
        menu.exec(self.diary_list.viewport().mapToGlobal(position))

    def start_save_timer(self):
        """在用户输入时启动保存计时器"""
        if self.current_file:  # 只有选择了日记才进行保存
            self.save_timer.start()

    def auto_save(self):
        """自动保存日记"""
        if not self.current_file:
            return
        content = self.diary_content.get_content()
        file_path = f"{DIARY_DIR}/{self.current_file}.enc"

        try:
            encrypted_data = EncryptionUtil.encrypt(content.encode(), self.key)
            with open(file_path, "wb") as file:
                file.write(encrypted_data)
        except Exception as e:
            MessageUtil.show_error_message(f"自动保存失败：{str(e)}")

    @staticmethod
    def load_key():
        key_file = CommonUtil.get_diary_key_path()
        if  os.path.exists(key_file):
            with open(key_file, "rb") as file:
                return file.read()


    def load_diary_list(self):
        """加载日记列表并按修改时间倒序排序"""
        self.diary_list.clear()
        diaries_path = CommonUtil.get_diary_enc_path()

        # 获取所有 .enc 文件及其修改时间
        diaries = [
            (file_name[:-4], os.path.getmtime(os.path.join(diaries_path, file_name)))
            for file_name in os.listdir(diaries_path)
            if file_name.endswith(".enc")
        ]

        # 按修改时间倒序排序
        diaries.sort(key=lambda x: x[1], reverse=True)

        # 添加到列表
        for file_name, _ in diaries:
            self.diary_list.addItem(file_name)

        # 默认选择第一个日记并加载内容
        if self.diary_list.count() > 0:
            first_item = self.diary_list.item(0)
            self.diary_list.setCurrentItem(first_item)
            self.load_diary(first_item)


    def load_diary(self, item):
        """加载选中的日记"""
        # 自动保存当前日记内容
        if self.current_file:
            self.auto_save()

        # 获取选中的日记文件名
        self.current_file = item.text()
        file_path = f"{DIARY_DIR}/{self.current_file}.enc"

        # 检查文件是否存在
        if not os.path.exists(file_path):
            MessageUtil.show_warning_message(f"日记文件不存在：{file_path}")
            self.diary_list.takeItem(self.diary_list.row(item))
            self.current_file = None
            return


        # 如果 Markdown 编辑器在预览模式，切换回编辑模式
        if self.diary_content.is_preview_mode():
            self.diary_content.switch_to_edit()


        # 加载并显示日记内容
        try:
            with open(file_path, "rb") as file:
                encrypted_data = file.read()
                content = EncryptionUtil.decrypt(encrypted_data, self.key).decode()
                self.diary_content.set_content(content)
        except Exception as e:
            MessageUtil.show_error_message(f"无法加载日记：{str(e)}")
            self.diary_list.takeItem(self.diary_list.row(item))
            self.current_file = None

    def new_diary(self):
        """新建日记"""
        file_name, ok = QInputDialog.getText(self, "新建日记", "请输入日记标题：")
        if ok and file_name:
            self.current_file = file_name
            file_path = f"{DIARY_DIR}/{self.current_file}.enc"

            # 如果文件已存在，提示用户选择其他名称
            if os.path.exists(file_path):
                MessageUtil.show_warning_message("同名日记已存在，请使用其他名称。")
                return

            # 创建一个空的加密文件
            try:
                encrypted_data = EncryptionUtil.encrypt("".encode(), self.key)
                with open(file_path, "wb") as file:
                    file.write(encrypted_data)

            except Exception as e:
                MessageUtil.show_error_message(f"无法创建新日记文件：{str(e)}")
                return

            # 重新加载列表（新建的文件会自动排在第一位）
            self.load_diary_list()

            # 自动选中新建条目
            first_item = self.diary_list.item(0)
            self.diary_list.setCurrentItem(first_item)
            self.diary_content.clear_content()

            MessageUtil.show_success_message(f"已创建新日记：{file_name}")

    def save_diary(self):
        content = self.diary_content.get_content()
        if not content:
            MessageUtil.show_warning_message("日记内容不能为空！")
            return
        file_name, ok = QInputDialog.getText(self, "保存日记", "请输入日记标题：")
        if ok and file_name:
            try:
                encrypted_data = EncryptionUtil.encrypt(content.encode(), self.key)
                with open(f"{DIARY_DIR}/{file_name}.enc", "wb") as file:
                    file.write(encrypted_data)
                self.load_diary_list()
                MessageUtil.show_success_message("日记已保存！")
            except Exception as e:
                MessageUtil.show_error_message(f"无法保存日记：{str(e)}")

    def delete_diary(self):
        """删除日记"""
        selected_item = self.diary_list.currentItem()
        if not selected_item:
            MessageUtil.show_warning_message("请先选择一篇日记！")
            return
        # 确认是否删除
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除日记 '{selected_item.text()}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            file_name = selected_item.text()
            file_path = f"{DIARY_DIR}/{file_name}.enc"

            # 删除文件
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    MessageUtil.show_success_message(f"已删除日记：{file_name}")
                else:
                    MessageUtil.show_warning_message(f"文件不存在：{file_path}")

                # 从列表中移除对应项
                self.diary_list.takeItem(self.diary_list.row(selected_item))

                # 如果删除的是当前日记，清空编辑框
                if self.current_file == file_name:
                    self.current_file = None
                    self.diary_content.clear_content()
            except Exception as e:
                MessageUtil.show_error_message(f"删除日记失败：{str(e)}")

    def rename_diary(self):
        """重命名选中的日记"""
        # 获取当前选中的列表项
        current_item = self.diary_list.currentItem()
        if not current_item:
            MessageUtil.show_warning_message("请先选择要重命名的日记！")
            return

        old_name = current_item.text()
        old_file_path = f"{DIARY_DIR}/{old_name}.enc"

        # 输入新的文件名
        new_name, ok = QInputDialog.getText(self, "重命名日记", "请输入新的日记名称：", text=old_name)
        if not ok or not new_name:
            return  # 用户取消操作或输入为空

        # 检查是否重名
        new_file_path = f"{DIARY_DIR}/{new_name}.enc"
        if os.path.exists(new_file_path):
            MessageUtil.show_warning_message("文件名已存在，请使用其他名称。")
            return

        # 重命名文件
        try:
            os.rename(old_file_path, new_file_path)

            # 更新列表项显示名称
            current_item.setText(new_name)

            # 如果重命名的是当前正在编辑的文件，更新 self.current_file
            if self.current_file == old_name:
                self.current_file = new_name

            MessageUtil.show_success_message(f"日记已重命名为：{new_name}")
        except Exception as e:
            MessageUtil.show_error_message(f"重命名失败：{str(e)}")

    def export_to_pdf(self):
        """将Markdown内容导出为PDF"""
        if not self.current_file:
            MessageUtil.show_warning_message("请先选择一篇日记！")
            return

        # # 检查Markdown编辑器是否处于预览模式
        if not self.diary_content.is_preview_mode():
            MessageUtil.show_warning_message("请切换到预览模式再进行导出！")
            return

        # 弹出保存文件对话框，让用户选择保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出为 PDF",
            f"{self.current_file}.pdf",
            "PDF 文件 (*.pdf)"
        )

        if not file_path:  # 用户取消操作
            return

        # 获取HTML内容的回调函数
        def handle_html_content(html_content):
            try:
                if not html_content.strip():
                    MessageUtil.show_warning_message("当前内容为空，无法导出为PDF！")
                    return
                font_config = FontConfiguration()
                html = HTML(string=html_content)
                css = CSS(string=f'''
                    @font-face {{
                        font-family: CustomFont;
                        src: url({CommonUtil.get_resource_path(FsConstants.FONT_FILE_PATH)});
                    }}
                    body {{ font-family: CustomFont }}''', font_config=font_config)
                html.write_pdf(
                    file_path, stylesheets=[css],
                    font_config=font_config)
                # 使用WeasyPrint将HTML导出为PDF
                HTML(string=html_content).write_pdf(file_path)
                MessageUtil.show_success_message(f"已成功导出 PDF：{file_path}")
            except Exception as e:
                MessageUtil.show_error_message(f"导出 PDF 失败：{str(e)}")

        # 获取HTML内容
        self.diary_content.get_preview_html(handle_html_content)


    def closeEvent(self, event):
        self.auto_save()
        # 调用父类关闭事件
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication([])
    window = DiaryApp()
    window.show()
    app.exec()

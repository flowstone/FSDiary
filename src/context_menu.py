from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QMessageBox, QInputDialog, QFileDialog
import os
from src.util.message_util import MessageUtil
from src.util.encryption_util import EncryptionUtil
from src.util.common_util import CommonUtil
from src.const.fs_constants import FsConstants
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


class DiaryContextMenu(QMenu):
    # 定义一个信号，用于通知当前文件已被删除
    current_file_deleted = Signal()
    def __init__(self, parent, diary_list, diary_content, current_file, key, diary_dir):
        super().__init__(parent)
        self.diary_list = diary_list
        self.diary_content = diary_content
        self.current_file = current_file
        self.key = key
        self.diary_dir = diary_dir

        # 删除选项
        delete_action = QAction("删除日记", self)
        delete_action.triggered.connect(self.delete_diary)
        self.addAction(delete_action)

        # 重命名选项
        rename_action = QAction("重命名日记", self)
        rename_action.triggered.connect(self.rename_diary)
        self.addAction(rename_action)

        # 导出成 PDF 选项
        export_pdf_action = QAction("导出成PDF", self)
        export_pdf_action.triggered.connect(self.export_to_pdf)
        self.addAction(export_pdf_action)

    def delete_diary(self):
        """删除日记"""
        selected_item = self.diary_list.currentItem()
        if not selected_item:
            MessageUtil.show_warning_message("请先选择一篇日记！")
            return
        # 确认是否删除
        reply = QMessageBox.question(
            self.parentWidget(),
            "确认删除",
            f"确定要删除日记 '{selected_item.text()}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            file_name = selected_item.text()
            file_path = f"{self.diary_dir}/{file_name}.enc"

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
                    # 发射信号
                    self.current_file_deleted.emit()
                    print("Signal current_file_deleted emitted.")

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
        old_file_path = f"{self.diary_dir}/{old_name}.enc"

        # 输入新的文件名
        new_name, ok = QInputDialog.getText(self.parentWidget(), "重命名日记", "请输入新的日记名称：", text=old_name)
        if not ok or not new_name:
            return  # 用户取消操作或输入为空

        # 检查是否重名
        new_file_path = f"{self.diary_dir}/{new_name}.enc"
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

        # 检查Markdown编辑器是否处于预览模式
        if not self.diary_content.is_preview_mode():
            MessageUtil.show_warning_message("请切换到预览模式再进行导出！")
            return

        # 弹出保存文件对话框，让用户选择保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self.parentWidget(),
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
                MessageUtil.show_success_message(f"已成功导出 PDF：{file_path}")
            except Exception as e:
                MessageUtil.show_error_message(f"导出 PDF 失败：{str(e)}")

        # 获取HTML内容
        self.diary_content.get_preview_html(handle_html_content)
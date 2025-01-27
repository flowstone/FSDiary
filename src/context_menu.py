from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QMessageBox, QInputDialog, QFileDialog, QLineEdit, QListWidgetItem
import os

from fs_base.message_util import MessageUtil
from loguru import logger

from src.util.common_util import CommonUtil
from src.const.fs_constants import FsConstants
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


class DiaryContextMenu(QMenu):
    expand_folder_signal = Signal(QListWidgetItem)

    def __init__(self, parent, diary_tree, diary_content, current_file, key, diary_dir, load_expand_folder):
        super().__init__(parent)
        self.diary_tree = diary_tree
        self.diary_content = diary_content
        self.current_file = current_file
        self.key = key
        self.diary_dir = diary_dir

        # 动态绑定槽函数
        self.expand_folder_signal.connect(load_expand_folder)

        selected_item = self.diary_tree.currentItem()
        self.file_path = selected_item.data(0, Qt.ItemDataRole.UserRole)
        # 添加新建文件夹选项
        create_folder_action = QAction(QIcon(CommonUtil.get_resource_path(FsConstants.FOLDER_ADD_RIGHT_MENU_PATH)), "新建文件夹", self)
        create_folder_action.triggered.connect(self.create_folder)
        self.addAction(create_folder_action)
        self.addSeparator()  # 分隔线

        """设置工具栏"""
        if selected_item and os.path.isdir(self.file_path):
            logger.info(f"{CommonUtil.get_resource_path(FsConstants.FOLDER_RENAME_RIGHT_MENU_PATH)}")
            rename_folder_action = QAction(QIcon(CommonUtil.get_resource_path(FsConstants.FOLDER_RENAME_RIGHT_MENU_PATH)), "重命名文件夹", self)
            rename_folder_action.triggered.connect(self.rename_folder)  # 绑定重命名文件夹的操作
            self.addAction(rename_folder_action)
            self.addSeparator()  # 分隔线

        if selected_item and os.path.isfile(self.file_path):
            # 重命名选项
            rename_action = QAction(QIcon(CommonUtil.get_resource_path(FsConstants.FILE_RENAME_RIGHT_MENU_PATH)), "重命名日记", self)
            rename_action.triggered.connect(self.rename_diary)
            self.addAction(rename_action)
            self.addSeparator()  # 分隔线

            # 添加删除选项
            delete_action = QAction(QIcon(CommonUtil.get_resource_path(FsConstants.FILE_REMOVE_RIGHT_MENU_PATH)), "删除日记", self)
            delete_action.triggered.connect(self.delete_diary)
            self.addAction(delete_action)
            self.addSeparator()  # 分隔线

            # 导出PDF选项（仅适用于文件）
            export_pdf_action = QAction(QIcon(CommonUtil.get_resource_path(FsConstants.PDF_RIGHT_MENU_PATH)), "导出成PDF", self)
            export_pdf_action.triggered.connect(self.export_to_pdf)
            self.addAction(export_pdf_action)

    def create_folder(self):
        """新建文件夹"""

        selected_item = self.diary_tree.currentItem()
        parent_path = selected_item.data(0, Qt.ItemDataRole.UserRole) if selected_item else self.diary_dir

        folder_name, ok = QInputDialog.getText(self, "新建文件夹", "请输入文件夹名称：")
        if ok and folder_name:
            new_folder_path = os.path.join(parent_path, folder_name)
            try:
                os.makedirs(new_folder_path, exist_ok=True)
                logger.info(f"成功创建文件夹：{folder_name}")

                self.expand_folder_signal.emit(selected_item)
            except Exception as e:
                logger.error(f"创建文件夹失败：{str(e)}")
                MessageUtil.show_error_message(f"创建文件夹失败：{str(e)}")

    def rename_folder(self):
        """重命名选中的文件夹"""
        selected_item = self.diary_tree.currentItem()
        if not selected_item:
            MessageUtil.show_warning_message("请先选择一个文件夹！")
            return

        # 获取选中项的路径
        folder_path = selected_item.data(0, Qt.ItemDataRole.UserRole)

        if not os.path.isdir(folder_path):
            MessageUtil.show_warning_message("选中的不是文件夹！")
            return

        # 弹出对话框让用户输入新的文件夹名称
        new_name, ok = QInputDialog.getText(self, "重命名文件夹", "请输入新的文件夹名称:", QLineEdit.EchoMode.Normal,
                                            selected_item.text(0))

        if ok and new_name:
            new_folder_path = os.path.join(os.path.dirname(folder_path), new_name)

            try:
                os.rename(folder_path, new_folder_path)  # 重命名文件夹

                # 更新树形结构
                selected_item.setText(0, new_name)  # 更新显示的文件夹名称
                selected_item.setData(0, Qt.ItemDataRole.UserRole, new_folder_path)  # 更新文件夹路径
                self.expand_folder_signal.emit(selected_item)

                logger.info(f"文件夹 '{folder_path}' 已重命名为 '{new_folder_path}'")
            except Exception as e:
                logger.error(f"重命名文件夹失败：{str(e)}")
                MessageUtil.show_error_message(f"重命名文件夹失败")


    def delete_diary(self):
        """删除日记"""
        selected_item = self.diary_tree.currentItem()
        if not selected_item:
            MessageUtil.show_warning_message("请先选择一篇日记！")
            return
        # 获取选中项的路径
        file_path = selected_item.data(0, Qt.ItemDataRole.UserRole)

        # 确认是否删除
        diary_name = selected_item.text(0)  # 传入 0 来获取第一列的文本
        # 确认是否删除
        reply = QMessageBox.question(
            self.parentWidget(),
            "确认删除",
            f"确定要删除日记 '{diary_name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # 删除文件
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    MessageUtil.show_success_message(f"已删除日记")
                else:
                    MessageUtil.show_warning_message(f"文件不存在")

                # 从树形结构中移除对应项
                parent_item = selected_item.parent()
                if parent_item:
                    parent_item.removeChild(selected_item)
                else:
                    self.diary_tree.takeTopLevelItem(self.diary_tree.indexOfTopLevelItem(selected_item))
                self.expand_folder_signal.emit(selected_item)

                # 如果删除的是当前日记，清空编辑框
                if self.current_file == diary_name:
                    self.current_file = None
                    self.diary_content.clear_content()


            except Exception as e:
                logger.error(f"删除日记失败：{str(e)}")
                MessageUtil.show_error_message(f"删除日记失败")

    def rename_diary(self):
        """重命名选中的日记"""
        # 获取当前选中的列表项
        current_item = self.diary_tree.currentItem()
        if not current_item:
            MessageUtil.show_warning_message("请先选择要重命名的日记！")
            return

        # 确保选中的项是文件，而不是文件夹
        if os.path.isdir(self.file_path):
            MessageUtil.show_warning_message("无法重命名文件夹！")
            return

        old_name = current_item.text(0)

        # 输入新的文件名
        new_name, ok = QInputDialog.getText(self.parentWidget(), "重命名日记", "请输入新的日记名称：", text=old_name)
        if not ok or not new_name:
            return  # 用户取消操作或输入为空

        # 检查是否重名
        # 修正路径构造：获取原文件的父目录
        parent_dir = os.path.dirname(self.file_path)  # 新增关键行
        base_name = os.path.splitext(new_name)[0]
        new_file_path = os.path.join(parent_dir, f"{base_name}.enc")
        if os.path.exists(new_file_path):
            MessageUtil.show_warning_message("文件名已存在，请使用其他名称。")
            return

        # 重命名文件
        try:
            os.rename(self.file_path, new_file_path)

            # 更新列表项显示名称
            current_item.setText(0, new_name)

            # 如果重命名的是当前正在编辑的文件，更新 self.current_file
            if self.current_file == old_name:
                self.current_file = new_name
                # 同步更新文件路径（关键）
                self.file_path = new_file_path  # 假设上下文菜单的 parent 是 DiaryApp

            # 新增：立即更新父目录的显示
            parent_item = current_item.parent()
            if parent_item:
                self.expand_folder_signal.emit(parent_item)
            MessageUtil.show_success_message(f"日记已重命名")
        except Exception as e:
            logger.error(f"重命名失败：{str(e)}")
            MessageUtil.show_error_message(f"重命名失败")



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
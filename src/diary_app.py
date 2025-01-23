from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QListWidget, \
    QMessageBox, QInputDialog, QWidget, QMenu, QSplitter, QFileDialog, QAbstractItemView, QTreeWidget, QTreeWidgetItem, \
    QLineEdit
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
            QApplication.quit()

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
        # 主界面布局
        main_layout = QHBoxLayout()
        # 添加分割器
        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)

        # 左侧布局（按钮 + 树形列表）
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # 新建日记按钮
        add_button = QPushButton("新建日记")
        add_button.clicked.connect(self.new_diary)
        left_layout.addWidget(add_button)

        # 左侧树形结构
        self.diary_tree = QTreeWidget()
        self.diary_tree.setHeaderHidden(True)  # 隐藏标题栏
        self.diary_tree.itemClicked.connect(self.load_diary_or_folder)
        self.diary_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.diary_tree.customContextMenuRequested.connect(self.show_context_menu)
        left_layout.addWidget(self.diary_tree)

        # 将左侧布局添加到分割器
        self.splitter.addWidget(left_widget)

        # 右侧编辑框
        self.diary_content = MarkdownEditor()
        self.diary_content.setObjectName("markdown_editor")
        self.diary_content.textChanged.connect(self.start_save_timer)  # 监听文本修改
        self.splitter.addWidget(self.diary_content)

        # 设置分割器的比例
        self.splitter.setStretchFactor(0, 2)  # 左侧占比较小
        self.splitter.setStretchFactor(1, 5)  # 右侧占比较大

        # 添加分割器到主布局
        main_layout.addWidget(self.splitter)

        self.setLayout(main_layout)

        self.load_diary_tree()

        self.diary_tree.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

    def load_diary_tree(self):
        """加载树形结构的根目录"""
        self.diary_tree.clear()
        root_item = QTreeWidgetItem(self.diary_tree, [os.path.basename(DIARY_DIR)])
        root_item.setData(0, Qt.ItemDataRole.UserRole, DIARY_DIR)
        root_item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)  # 标记可展开
        self.diary_tree.addTopLevelItem(root_item)

    @staticmethod
    def expand_folder(item):
        """按需加载子目录和文件"""
        folder_path = item.data(0, Qt.ItemDataRole.UserRole)
        if not folder_path or not os.path.isdir(folder_path):
            return
        item.takeChildren()  # 清除旧子节点

        # 加载子目录和文件
        try:
            for entry in os.scandir(folder_path):
                #logger.info(f"处理条目：{entry.name}, 路径：{entry.path}")  # 调试输出
                if entry.is_dir():
                    child_item = QTreeWidgetItem(item, [entry.name])
                    child_item.setData(0, Qt.ItemDataRole.UserRole, entry.path)  # 设置子目录路径
                    child_item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
                elif entry.is_file() and entry.name.endswith(".enc"):
                    child_item = QTreeWidgetItem(item, [entry.name[:-4]])  # 去掉扩展名显示
                    child_item.setData(0, Qt.ItemDataRole.UserRole, entry.path)  # 设置文件路径
        except Exception as e:
            MessageUtil.show_error_message(f"加载目录失败：{str(e)}")

    def show_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu()
        selected_item = self.diary_tree.currentItem()

        # 添加新建文件夹选项
        create_folder_action = QAction("新建文件夹", self)
        create_folder_action.triggered.connect(self.create_folder)
        menu.addAction(create_folder_action)
        """设置工具栏"""
        if selected_item and  os.path.isdir(selected_item.data(0, Qt.ItemDataRole.UserRole)):
            rename_folder_action = QAction("重命名文件夹", self)
            rename_folder_action.triggered.connect(self.rename_folder)  # 绑定重命名文件夹的操作
            menu.addAction(rename_folder_action)

        if selected_item and  os.path.isfile(selected_item.data(0, Qt.ItemDataRole.UserRole)):
            # 重命名选项
            rename_action = QAction("重命名日记", self)
            rename_action.triggered.connect(self.rename_diary)
            menu.addAction(rename_action)
            # 添加删除选项
            delete_action = QAction("删除日记", self)
            delete_action.triggered.connect(self.delete_diary)
            menu.addAction(delete_action)
            # 导出PDF选项（仅适用于文件）
            export_pdf_action = QAction("导出成PDF", self)
            export_pdf_action.triggered.connect(self.export_to_pdf)
            menu.addAction(export_pdf_action)

        # 在树形结构中显示右键菜单
        menu.exec(self.diary_tree.viewport().mapToGlobal(position))

    def create_folder(self):
        """新建文件夹"""
        selected_item = self.diary_tree.currentItem()
        parent_path = selected_item.data(0, Qt.ItemDataRole.UserRole) if selected_item else DIARY_DIR

        folder_name, ok = QInputDialog.getText(self, "新建文件夹", "请输入文件夹名称：")
        if ok and folder_name:
            new_folder_path = os.path.join(parent_path, folder_name)
            try:
                os.makedirs(new_folder_path, exist_ok=True)
                logger.info(f"成功创建文件夹：{folder_name}")
                self.expand_folder(selected_item)
            except Exception as e:
                logger.error(f"创建文件夹失败：{str(e)}")
                MessageUtil.show_error_message(f"创建文件夹失败：{str(e)}")

    def load_diary_or_folder(self, item):
        """加载选中的日记或展开文件夹"""
        self.file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if not self.file_path:  # 检查路径是否为 None 或空值
            MessageUtil.show_error_message("路径无效或丢失！")
            return

        if os.path.isdir(self.file_path):
            self.expand_folder(item)
        else:
            self.load_diary(item)

    def start_save_timer(self):
        """在用户输入时启动保存计时器"""
        if self.current_file:  # 只有选择了日记才进行保存
            self.save_timer.start()

    def auto_save(self):
        """自动保存日记"""
        if not self.current_file or os.path.isdir(self.current_file):
            return
        content = self.diary_content.get_content()

        try:
            encrypted_data = EncryptionUtil.encrypt(content.encode(), self.key)
            with open(self.current_file, "wb") as file:
                file.write(encrypted_data)
        except Exception as e:
            MessageUtil.show_error_message(f"自动保存失败：{str(e)}")

    @staticmethod
    def load_key():
        key_file = CommonUtil.get_diary_key_path()
        if  os.path.exists(key_file):
            with open(key_file, "rb") as file:
                return file.read()



    def load_diary(self, item):
        """加载选中的日记"""
        # 自动保存当前日记内容
        if self.current_file:
            self.auto_save()

        # 获取选中的日记文件路径
        self.current_file = self.file_path

        # 检查文件是否存在
        if not os.path.exists(self.file_path):
            logger.info(f"日记文件不存在：{self.file_path}")
            MessageUtil.show_warning_message(f"日记文件不存在")
            parent_item = item.parent()
            if parent_item:
                parent_item.removeChild(item)
            else:
                self.diary_tree.takeTopLevelItem(self.diary_tree.indexOfTopLevelItem(item))
            self.current_file = None
            return

        # 如果 Markdown 编辑器在预览模式，切换回编辑模式
        if self.diary_content.is_preview_mode():
            self.diary_content.switch_to_edit()

        # 加载并显示日记内容
        try:
            with open(self.file_path, "rb") as file:
                encrypted_data = file.read()
                content = EncryptionUtil.decrypt(encrypted_data, self.key).decode()
                self.diary_content.set_content(content)
        except Exception as e:
            logger.error(f"无法加载日记：{str(e)}")
            MessageUtil.show_error_message(f"无法加载日记")
            parent_item = item.parent()
            if parent_item:
                parent_item.removeChild(item)
            else:
                self.diary_tree.takeTopLevelItem(self.diary_tree.indexOfTopLevelItem(item))
            self.current_file = None

    def new_diary(self):
        """新建日记"""
        # 提示用户输入日记标题
        file_name, ok = QInputDialog.getText(self, "新建日记", "请输入日记标题：")
        if not ok or not file_name.strip():
            return  # 用户取消或未输入内容
        self.current_file = file_name.strip()
        selected_item = self.diary_tree.currentItem()
        if not selected_item:
            file_path = f"{DIARY_DIR}/{self.current_file}.enc"
        # 获取选中项的路径
        else:
            select_file_path = selected_item.data(0, Qt.ItemDataRole.UserRole)
            if os.path.isdir(select_file_path):
                file_path = f"{select_file_path}/{self.current_file}.enc"
            else:
                file_path = f"{os.path.dirname(select_file_path)}/{self.current_file}.enc"

        logger.info(f"当前创建文件的全路径:{file_path}")
        # 检查同名文件是否已存在
        if os.path.exists(file_path):
            MessageUtil.show_warning_message("同名日记已存在，请使用其他名称。")
            return

        # 创建一个空的加密文件
        try:
            encrypted_data = EncryptionUtil.encrypt("".encode(), self.key)  # 加密空字符串
            with open(file_path, "wb") as file:
                file.write(encrypted_data)
        except Exception as e:
            logger.error(f"无法创建新日记文件：{str(e)}")
            MessageUtil.show_error_message(f"无法创建新日记文件")
            return

        # 重新加载日记列表
        self.load_diary_tree()

        # 在树形控件中选中新建的日记
        item = self.find_diary_item(file_path)
        if item:
            self.diary_tree.setCurrentItem(item)

        # 清空内容编辑器
        self.diary_content.clear_content()

        # 成功提示
        logger.info(f"已创建新日记：{self.current_file}")

    def find_diary_item(self, file_path):
        """根据文件路径找到对应的树形控件条目"""
        root = self.diary_tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            if item.data(0, Qt.ItemDataRole.UserRole) == file_path:
                return item
        return None

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
                    # 更新日记列表
                    self.load_diary_tree()

                MessageUtil.show_success_message("日记已保存！")
            except Exception as e:
                logger.error(f"无法保存日记：{str(e)}")
                MessageUtil.show_error_message(f"无法保存日记")

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
        reply = QMessageBox.question(
            self,
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
            os.rename(self.file_path, new_file_path)

            # 更新列表项显示名称
            current_item.setText(0, new_name)

            # 如果重命名的是当前正在编辑的文件，更新 self.current_file
            if self.current_file == old_name:
                self.current_file = new_name

            MessageUtil.show_success_message(f"日记已重命名")
        except Exception as e:
            logger.error(f"重命名失败：{str(e)}")
            MessageUtil.show_error_message(f"重命名失败")

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
                MessageUtil.show_success_message(f"已成功导出PDF")
            except Exception as e:
                logger.error(f"导出 PDF 失败：{str(e)}")
                MessageUtil.show_error_message(f"导出PDF失败")

        # 获取HTML内容
        self.diary_content.get_preview_html(handle_html_content)

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

                logger.info(f"文件夹 '{folder_path}' 已重命名为 '{new_folder_path}'")
            except Exception as e:
                logger.error(f"重命名文件夹失败：{str(e)}")
                MessageUtil.show_error_message(f"重命名文件夹失败")

    def closeEvent(self, event):
        self.auto_save()
        # 调用父类关闭事件
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication([])
    window = DiaryApp()
    window.show()
    app.exec()

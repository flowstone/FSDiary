import sys

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QListWidget, \
    QMessageBox, QInputDialog, QWidget, QMenu, QSplitter, QFileDialog, QAbstractItemView, QTreeWidgetItem
from PySide6.QtCore import Qt, QTimer, QObject, Signal
import os

from fs_base import ConfigManager
from loguru import logger

from src.const.fs_constants import FsConstants
from src.context_menu import DiaryContextMenu
from src.option_webdav_sync import OptionWebDavSync
from src.ui_components import UiComponents
from src.util.common_util import CommonUtil
from src.util.encryption_util import EncryptionUtil
from fs_base.message_util import MessageUtil
from src.widget.markdown_editor import MarkdownEditor
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

DIARY_DIR = f"{CommonUtil.get_diary_article_path()}"

class DiaryApp(QWidget):
    init_connect_webdav_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("日记应用")
        self.config_manager = ConfigManager()
        self.config_manager.config_updated.connect(self.on_config_updated)
        # 加载加密密钥
        self.key = self.load_key()
        if not self.key:
            MessageUtil.show_error_message("无法加载密钥文件！")
            exit()

        # 初始化 WebDav 同步类
        self.webdav_sync = OptionWebDavSync()
        self.init_connect_webdav_signal.connect(self._handle_webdav_sync)

        # 当前日记文件
        self.current_file = None
        self.menu = None
        # 保存延迟计时器
        self.save_timer = QTimer()
        self.save_timer.setInterval(5000)  # 2 秒延迟
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.auto_save)

        self.init_ui()

    def init_ui(self):
        # 主界面布局
        main_layout = QHBoxLayout()
        # 使用封装的布局类
        self.diary_layout = UiComponents()
        add_button = self.diary_layout.add_button
        self.diary_tree = self.diary_layout.diary_tree
        self.diary_content = self.diary_layout.diary_content

        add_button.clicked.connect(self.new_diary)
        self.diary_tree.itemClicked.connect(self.load_diary_or_folder)
        self.diary_tree.customContextMenuRequested.connect(self.show_context_menu)
        self.diary_content.textChangedSignal.connect(self.start_save_timer)  # 监听文本修改


        main_layout.addWidget(self.diary_layout)
        self.setLayout(main_layout)
        self.load_diary_tree()
        self.webdav_auto_checked = self.config_manager.get_config(ConfigManager.WEBDAV_AUTO_CHECKED_KEY)
        if self.webdav_auto_checked:
            logger.info("---- WebDAV触发信号 ----")
            self.init_connect_webdav_signal.emit()

    def on_config_updated(self, key, value):
        if key == ConfigManager.WEBDAV_AUTO_CHECKED_KEY:
            self.webdav_auto_checked = value
    # 动态绑定信息用到的方法
    def load_expand_folder(self, item):
        self.expand_folder(item)

    def load_diary_tree(self):
        """加载树形结构的根目录"""
        self.diary_tree.clear()
        root_item = QTreeWidgetItem(self.diary_tree, [os.path.basename(DIARY_DIR)])
        root_item.setData(0, Qt.ItemDataRole.UserRole, DIARY_DIR)
        root_item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)  # 标记可展开
        root_item.setIcon(0, QIcon(CommonUtil.get_resource_path(FsConstants.ROOT_FOLDER_TREE_ICON_PATH)))
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
                # logger.info(f"处理条目：{entry.name}, 路径：{entry.path}")  # 调试输出
                if entry.is_dir():
                    child_item = QTreeWidgetItem(item, [entry.name])
                    child_item.setData(0, Qt.ItemDataRole.UserRole, entry.path)  # 设置子目录路径
                    child_item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
                    child_item.setIcon(0, QIcon(CommonUtil.get_resource_path(FsConstants.FOLDER_TREE_ICON_PATH)))

                elif entry.is_file() and entry.name.endswith(".enc"):
                    child_item = QTreeWidgetItem(item, [entry.name[:-4]])  # 去掉扩展名显示
                    child_item.setData(0, Qt.ItemDataRole.UserRole, entry.path)  # 设置文件路径
                    child_item.setIcon(0, QIcon(CommonUtil.get_resource_path(FsConstants.DIARY_TREE_ICON_PATH)))

        except Exception as e:
            logger.error(f"加载目录失败：{str(e)}")
            MessageUtil.show_error_message(f"加载目录失败")

    def show_context_menu(self, position):
         """显示右键菜单"""
         menu = DiaryContextMenu(self, self.diary_tree, self.diary_content, self.current_file, self.key, DIARY_DIR, self.load_expand_folder)
         menu.exec(self.diary_tree.viewport().mapToGlobal(position))

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
        if not self.current_file or os.path.isdir(self.file_path):
            return
        content = self.diary_content.get_content()

        try:
            encrypted_data = EncryptionUtil.encrypt(content.encode(), self.key)
            with open(self.file_path, "wb") as file:
                file.write(encrypted_data)
        except Exception as e:
            logger.error(f"自动保存失败：{str(e)}")
            MessageUtil.show_error_message("自动保存失败")

    @staticmethod
    def load_key():
        key_file = CommonUtil.get_diary_key_path()
        try:
            with open(key_file, "rb") as f:
                return f.read()
        except FileNotFoundError:
            logger.critical("密钥文件不存在")
            MessageUtil.show_error_message("密钥文件丢失，无法启动！")
            sys.exit(1)
        except Exception as e:
            logger.critical(f"读取密钥失败: {str(e)}")
            sys.exit(1)



    def load_diary(self, item):
        """加载选中的日记"""

        # 获取选中的日记文件路径
        # 直接从传入的item获取最新路径
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        self.current_file = item.text(0)
        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.info(f"日记文件不存在：{file_path}")
            MessageUtil.show_warning_message(f"日记文件不存在")

            self._remove_tree_item(item)
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

                # 更新当前文件路径（关键修复）
                self.file_path = file_path  # 同步更新实例变量
        except Exception as e:
            logger.error(f"无法加载日记：{str(e)}")
            MessageUtil.show_error_message(f"无法加载日记")
            self._remove_tree_item(item)
            self.current_file = None

    def new_diary(self):
        """新建日记"""
        file_name, ok = QInputDialog.getText(self, "新建日记", "请输入日记标题：")

        if not ok or not file_name.strip():
            return  # 用户取消或未输入内容

        self.current_file = file_name.strip()
        selected_item = self.diary_tree.currentItem()
        select_file_path = selected_item.data(0, Qt.ItemDataRole.UserRole)
        if not selected_item:
            file_path = f"{DIARY_DIR}/{self.current_file}.enc"
        # 获取选中项的路径
        else:
            select_file_path = selected_item.data(0, Qt.ItemDataRole.UserRole)
            # 获取父目录路径
            parent_dir = select_file_path if os.path.isdir(select_file_path) else os.path.dirname(select_file_path)
            # 使用 os.path.join 安全拼接路径
            file_path = os.path.join(parent_dir, f"{self.current_file}.enc")

        logger.info(f"当前创建文件的全路径:{file_path}")

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
            logger.error(f"无法创建新日记文件：{str(e)}")
            MessageUtil.show_error_message(f"无法创建新日记文件")
            return

        # 局部刷新父节点
        parent_item = selected_item if os.path.isdir(select_file_path) else selected_item.parent()
        self.expand_folder(parent_item)  # 重新展开父目录以加载新文件

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


    def closeEvent(self, event):
        self.auto_save()
        # 调用父类关闭事件
        super().closeEvent(event)

    def _remove_tree_item(self, item):
        """安全移除树节点"""
        if parent := item.parent():
            parent.removeChild(item)
        else:
            self.diary_tree.takeTopLevelItem(self.diary_tree.indexOfTopLevelItem(item))

    def _handle_webdav_sync(self):
        try:
            self.webdav_sync.signal_sync_webdav()
        except Exception as e:
            logger.error(f"WebDAV 同步失败: {str(e)}")
            MessageUtil.show_error_message("云同步失败，请检查网络和配置")
if __name__ == "__main__":
    app = QApplication([])
    window = DiaryApp()
    window.show()
    app.exec()

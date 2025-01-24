
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QLabel, QTextEdit, QFileDialog, QListWidget, QWidget, QMessageBox, QGroupBox, QCheckBox
)
from PySide6.QtCore import QTimer, Qt
from webdav3.client import Client
import os
from loguru import logger

from src.util.common_util import CommonUtil
from src.util.config_util import ConfigUtil
from src.util.message_util import MessageUtil
from src.widget.transparent_textbox_widget import TransparentTextBox


class OptionWebDavSync(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WebDAV 同步工具")
        self.setMinimumWidth(600)

        # WebDAV 配置
        self.auto_sync_checkbox = QCheckBox("自动同步")
        self.webdav_url = QLineEdit(self)
        self.webdav_username = QLineEdit(self)
        self.webdav_password = QLineEdit(self)
        self.local_dir = QLineEdit(self)
        self.remote_dir = QLineEdit(self)

        self.auto_sync_checkbox.setChecked(ConfigUtil.get_ini_sync_webdav_auto_checked())
        self.webdav_url.setText(ConfigUtil.get_ini_sync_webdav_param("sync.webdav.address"))
        self.webdav_username.setText(ConfigUtil.get_ini_sync_webdav_param("sync.webdav.username"))
        self.webdav_password.setText(ConfigUtil.get_ini_sync_webdav_param("sync.webdav.password"))
        local_dir = ConfigUtil.get_ini_sync_webdav_param("sync.webdav.remote_dir")
        self.local_dir.setText(local_dir if local_dir else CommonUtil.get_diary_enc_path())
        remote_dir = ConfigUtil.get_ini_sync_webdav_param("sync.webdav.remote_dir")
        self.remote_dir.setText(remote_dir if remote_dir else "/")

        self.auto_sync_checkbox.stateChanged.connect(self.on_checkbox_state_changed)
        self.webdav_url.textChanged.connect(lambda text: ConfigUtil.set_ini_sync_webdav_param("sync.webdav.address", text))
        self.webdav_username.textChanged.connect(lambda text: ConfigUtil.set_ini_sync_webdav_param("sync.webdav.username", text))
        self.webdav_password.textChanged.connect(lambda text: ConfigUtil.set_ini_sync_webdav_param("sync.webdav.password", text))
        self.local_dir.textChanged.connect(lambda text: ConfigUtil.set_ini_sync_webdav_param("sync.webdav.local_dir", text))
        self.remote_dir.textChanged.connect(lambda text: ConfigUtil.set_ini_sync_webdav_param("sync.webdav.remote_dir", text))

        # 初始化布局
        self.init_ui()

        # WebDAV 客户端
        self.client = None

        # 同步定时器
        self.sync_timer = QTimer(self)
        self.sync_timer.setInterval(60000)  # 每 1 分钟同步一次
        self.sync_timer.timeout.connect(self.sync_files)

    def init_ui(self):
        # 主布局
        main_layout = QVBoxLayout()

        # 配置布局
        linker_group_box = QGroupBox("连接设置")
        config_layout = QVBoxLayout()
        config_layout.addWidget(self.auto_sync_checkbox)
        config_layout.addWidget(QLabel("WebDAV 地址:"))
        config_layout.addWidget(self.webdav_url)
        config_layout.addWidget(QLabel("用户名:"))
        config_layout.addWidget(self.webdav_username)
        config_layout.addWidget(QLabel("密码:"))
        config_layout.addWidget(self.webdav_password)


        config_layout.addWidget(QLabel("远程目录:"))
        config_layout.addWidget(self.remote_dir)
        config_layout.addWidget(QLabel("本地目录:"))
        local_dir_layout = QHBoxLayout()
        local_dir_layout.addWidget(self.local_dir)
        select_dir_btn = QPushButton("选择目录", self)
        select_dir_btn.clicked.connect(self.select_local_directory)
        local_dir_layout.addWidget(select_dir_btn)
        config_layout.addLayout(local_dir_layout)
        linker_group_box.setLayout(config_layout)
        main_layout.addWidget(linker_group_box)



        # 按钮布局
        button_layout = QHBoxLayout()
        connect_btn = QPushButton("测试WebDAV", self)
        connect_btn.clicked.connect(self.connect_webdav)
        sync_btn = QPushButton("同步文件", self)
        sync_btn.clicked.connect(self.sync_files)

        button_layout.addWidget(connect_btn)
        button_layout.addWidget(sync_btn)

        main_layout.addLayout(button_layout)
        main_layout.addWidget(TransparentTextBox())

        self.setLayout(main_layout)


    def on_checkbox_state_changed(self, state):
        if state == 2:  # 2 表示选中状态
            url = self.webdav_url.text().strip()
            username = self.webdav_username.text().strip()
            password = self.webdav_password.text().strip()

            if not url or not username or not password:
                MessageUtil.show_warning_message("请填写完整的 WebDAV 配置")
                self.auto_sync_checkbox.setChecked(False)
                return

            self.start_auto_sync()
            ConfigUtil.set_ini_sync_webdav_auto_checked(True)
            logger.info("自动同步已开启")
        elif state == 0:  # 0 表示未选中状态
            self.stop_auto_sync()
            ConfigUtil.set_ini_sync_webdav_auto_checked(False)
            logger.info("自动同步已关闭")

    def select_local_directory(self):
        """选择本地目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择本地目录")
        if dir_path:
            self.local_dir.setText(dir_path)


    def connect_webdav(self):
        """连接 WebDAV"""
        logger.info("开启WebDAV同步")
        url = self.webdav_url.text().strip()
        username = self.webdav_username.text().strip()
        password = self.webdav_password.text().strip()

        if not url or not username or not password:
            MessageUtil.show_warning_message("请填写完整的 WebDAV 配置")
            return

        try:
            self.client = Client({
                "webdav_hostname": url,
                "webdav_login": username,
                "webdav_password": password,
            })
            MessageUtil.show_success_message("连接到 WebDAV 服务器")
        except Exception as e:
            MessageUtil.show_error_message("无法连接到 WebDAV 服务器")


    def sync_files(self):
        """同步文件"""
        local_dir = self.local_dir.text().strip()
        remote_dir = self.remote_dir.text().strip()
        if not os.path.exists(remote_dir):
            MessageUtil.show_warning_message("远程目录不存在")
            return
        if not os.path.exists(local_dir):
            MessageUtil.show_warning_message("本地目录不存在")
            return

        if not self.client:
            MessageUtil.show_warning_message("请先连接 WebDAV 服务器")
            return

        try:
            # 下载远程文件
            for file in self.client.list(remote_dir):
                remote_file_path = f"/{file}"
                local_file_path = os.path.join(local_dir, file)
                if not os.path.exists(local_file_path):
                    try:
                        with open(local_file_path, "wb") as f:
                            self.client.download_sync(remote_path=remote_file_path, local_path=local_file_path)
                        logger.info(f"下载文件: {file}")
                    except Exception as e:
                        logger.error(f"下载文件失败: {file}, 错误信息: {str(e)}")

            # 上传本地文件
            for file in os.listdir(local_dir):
                remote_file_path = f"/{file}"
                local_file_path = os.path.join(local_dir, file)
                try:
                    with open(local_file_path, "rb") as f:
                        self.client.upload_sync(remote_path=remote_file_path, local_path=local_file_path)
                    logger.info(f"上传文件: {file}")
                except Exception as e:
                    logger.error(f"上传文件失败: {file}, 错误信息: {str(e)}")

            logger.info("文件同步完成")
        except Exception as e:
            logger.warning(f"文件同步失败: {str(e)}")

    def start_auto_sync(self):
        """启动自动同步"""
        self.sync_timer.start()
        logger.info("自动同步已启动")

    def stop_auto_sync(self):
        """停止自动同步"""
        self.sync_timer.stop()
        logger.info("自动同步已停止")


if __name__ == "__main__":
    app = QApplication([])
    window = OptionWebDavSync()
    window.show()
    app.exec()

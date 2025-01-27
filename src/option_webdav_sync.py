
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QLabel, QTextEdit, QFileDialog, QListWidget, QWidget, QMessageBox, QGroupBox, QCheckBox
)
from PySide6.QtCore import QTimer, Qt
from fs_base.config_manager import ConfigManager
from fs_base.widget import TransparentTextBox
from webdav3.client import Client
import os
from loguru import logger

from src.const.fs_constants import FsConstants
from src.util.common_util import CommonUtil
from fs_base.message_util import MessageUtil


class OptionWebDavSync(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WebDAV 同步工具")
        self.setMinimumWidth(600)
        self.config_manager = ConfigManager()

        # WebDAV 配置
        self.auto_sync_checkbox = QCheckBox("自动同步")
        self.webdav_url = QLineEdit(self)
        self.webdav_username = QLineEdit(self)
        self.webdav_password = QLineEdit(self)
        self.local_dir = QLineEdit(self)
        self.remote_dir = QLineEdit(self)
        self.auto_sync_checkbox.setChecked(self.config_manager.get_config(FsConstants.WEBDAV_AUTO_CHECKED_KEY))
        self.webdav_url.setText(self.config_manager.get_config(FsConstants.WEBDAV_ADDRESS_KEY))
        self.webdav_username.setText(self.config_manager.get_config(FsConstants.WEBDAV_USERNAME_KEY))
        self.webdav_password.setText(self.config_manager.get_config(FsConstants.WEBDAV_PASSWORD_KEY))
        local_dir = self.config_manager.get_config(FsConstants.WEBDAV_LOCAL_DIR_KEY)
        self.local_dir.setText(local_dir if local_dir else CommonUtil.get_diary_enc_path())
        remote_dir = self.config_manager.get_config(FsConstants.WEBDAV_REMOTE_DIR_KEY)
        self.remote_dir.setText(remote_dir if remote_dir else "/")

        self.auto_sync_checkbox.stateChanged.connect(self.on_checkbox_state_changed)
        self.webdav_url.textChanged.connect(lambda text: self.config_manager.set_config(FsConstants.WEBDAV_ADDRESS_KEY, text))
        self.webdav_username.textChanged.connect(lambda text: self.config_manager.set_config(FsConstants.WEBDAV_USERNAME_KEY, text))
        self.webdav_password.textChanged.connect(lambda text: self.config_manager.set_config(FsConstants.WEBDAV_PASSWORD_KEY, text))
        self.local_dir.textChanged.connect(lambda text: self.config_manager.set_config(FsConstants.WEBDAV_LOCAL_DIR_KEY, text))
        self.remote_dir.textChanged.connect(lambda text: self.config_manager.set_config(FsConstants.WEBDAV_REMOTE_DIR_KEY, text))

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
            self.config_manager.set_config(FsConstants.WEBDAV_AUTO_CHECKED_KEY,True)
            logger.info("自动同步已开启")
        elif state == 0:  # 0 表示未选中状态
            self.stop_auto_sync()
            self.config_manager.set_config(FsConstants.WEBDAV_AUTO_CHECKED_KEY,False)
            logger.info("自动同步已关闭")

    def select_local_directory(self):
        """选择本地目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择本地目录")
        if dir_path:
            self.local_dir.setText(dir_path)


    def connect_webdav(self):
        """连接 WebDAV"""
        url = self.webdav_url.text().strip()
        username = self.webdav_username.text().strip()
        password = self.webdav_password.text().strip()

        if not url or not username or not password:
            MessageUtil.show_warning_message("请填写完整的 WebDAV 配置")
            return
        try:
            # 初始化 WebDAV 客户端
            self.client = Client({
                "webdav_hostname": url,
                "webdav_login": username,
                "webdav_password": password,
            })

            #测试连接，尝试列举根目录
            if self.client.list("/"):
                MessageUtil.show_success_message("成功连接到 WebDAV 服务器")
                # 成功连接后禁用输入框
                self.webdav_url.setEnabled(False)
                self.webdav_username.setEnabled(False)
                self.webdav_password.setEnabled(False)
            else:
                raise ConnectionError("无法列举 WebDAV 根目录，可能是权限不足")

        except ConnectionError as ce:
            logger.error(f"WebDAV 权限不足: {str(ce)}")
            MessageUtil.show_error_message(f"WebDAV 权限不足")
        except Exception as e:
            logger.error(f"无法连接到 WebDAV 服务器: {str(e)}")
            MessageUtil.show_error_message("无法连接到 WebDAV 服务器")

    def signal_sync_webdav(self):
        """连接 WebDAV"""
        url = self.webdav_url.text().strip()
        username = self.webdav_username.text().strip()
        password = self.webdav_password.text().strip()

        if not url or not username or not password:
            MessageUtil.show_warning_message("请填写完整的 WebDAV 配置")
            return
        try:
            # 初始化 WebDAV 客户端
            self.client = Client({
                "webdav_hostname": url,
                "webdav_login": username,
                "webdav_password": password,
            })

            # 测试连接，尝试列举根目录
            if not self.client.list("/"):
                logger.warning("无法列举 WebDAV 根目录，可能是权限不足")
                raise ConnectionError("无法列举 WebDAV 根目录，可能是权限不足")

            self.start_auto_sync()
        except ConnectionError as ce:
            logger.error(f"WebDAV 权限不足: {str(ce)}")
            MessageUtil.show_error_message(f"WebDAV 权限不足")
        except Exception as e:
            logger.error(f"无法连接到 WebDAV 服务器: {str(e)}")
            MessageUtil.show_error_message("无法连接到 WebDAV 服务器")

    def sync_files(self):
        """同步文件（支持文件夹，并自动创建文件夹）"""
        local_dir = self.local_dir.text().strip()
        remote_dir = self.remote_dir.text().strip()

        if not os.path.exists(local_dir):
            MessageUtil.show_warning_message("本地目录不存在")
            return
        if not self.client:
            MessageUtil.show_warning_message("请先连接 WebDAV 服务器")
            return

        try:
            # 下载远程目录到本地
            self.sync_remote_to_local(remote_dir, local_dir)

            # 上传本地目录到远程
            self.sync_local_to_remote(local_dir, remote_dir)

            logger.info("文件同步完成")
        except Exception as e:
            logger.error(f"文件同步失败: {str(e)}")

    def sync_remote_to_local(self, remote_dir, local_dir):
        """递归下载远程目录到本地，并创建本地文件夹"""
        try:
            # 确保本地目录存在
            os.makedirs(local_dir, exist_ok=True)

            # 获取远程目录内容
            for item in self.client.list(remote_dir):
                remote_path = f"{remote_dir}/{item}"
                local_path = os.path.join(local_dir, item)

                # 判断是否是文件夹
                if self.client.is_dir(remote_path):
                    # 创建本地文件夹并递归下载
                    logger.info(f"创建本地文件夹: {local_path}")
                    self.sync_remote_to_local(remote_path, local_path)
                else:
                    # 下载文件
                    try:
                        with open(local_path, "wb") as f:
                            self.client.download_sync(remote_path=remote_path, local_path=local_path)
                        logger.info(f"下载文件: {remote_path} -> {local_path}")
                    except Exception as e:
                        logger.error(f"下载文件失败: {remote_path}, 错误信息: {str(e)}")
        except Exception as e:
            logger.error(f"下载远程目录失败: {remote_dir}, 错误信息: {str(e)}")

    def sync_local_to_remote(self, local_dir, remote_dir):
        """递归上传本地目录到远程，并创建远程文件夹"""
        try:
            # 确保远程目录存在
            if not self.client.check(remote_dir):
                self.client.mkdir(remote_dir)
                logger.info(f"创建远程文件夹: {remote_dir}")

            # 遍历本地目录内容
            for item in os.listdir(local_dir):
                local_path = os.path.join(local_dir, item)
                remote_path = f"{remote_dir}/{item}"

                if os.path.isdir(local_path):
                    # 如果是文件夹，递归上传
                    logger.info(f"创建远程文件夹: {remote_path}")
                    self.sync_local_to_remote(local_path, remote_path)
                else:
                    # 上传文件
                    try:
                        with open(local_path, "rb") as f:
                            self.client.upload_sync(remote_path=remote_path, local_path=local_path)
                        logger.info(f"上传文件: {local_path} -> {remote_path}")
                    except Exception as e:
                        logger.error(f"上传文件失败: {local_path}, 错误信息: {str(e)}")
        except Exception as e:
            logger.error(f"上传本地目录失败: {local_dir}, 错误信息: {str(e)}")

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

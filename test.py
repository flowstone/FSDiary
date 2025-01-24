from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QLabel, QTextEdit, QFileDialog, QListWidget, QWidget, QMessageBox
)
from PySide6.QtCore import QTimer, Qt
from webdav3.client import Client
import os

class WebDavSyncTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WebDAV 同步工具")
        self.setGeometry(100, 100, 800, 600)

        # WebDAV 配置
        self.webdav_url = QLineEdit(self)
        self.webdav_username = QLineEdit(self)
        self.webdav_password = QLineEdit(self)
        self.local_dir = QLineEdit(self)

        # 日志区域
        self.log_area = QTextEdit(self)
        self.log_area.setReadOnly(True)

        # 文件列表
        self.remote_files = QListWidget(self)
        self.local_files = QListWidget(self)

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
        config_layout = QVBoxLayout()
        config_layout.addWidget(QLabel("WebDAV 地址:"))
        config_layout.addWidget(self.webdav_url)
        config_layout.addWidget(QLabel("用户名:"))
        config_layout.addWidget(self.webdav_username)
        config_layout.addWidget(QLabel("密码:"))
        config_layout.addWidget(self.webdav_password)
        config_layout.addWidget(QLabel("本地目录:"))
        local_dir_layout = QHBoxLayout()
        local_dir_layout.addWidget(self.local_dir)
        select_dir_btn = QPushButton("选择目录", self)
        select_dir_btn.clicked.connect(self.select_local_directory)
        local_dir_layout.addWidget(select_dir_btn)
        config_layout.addLayout(local_dir_layout)
        main_layout.addLayout(config_layout)

        # 文件列表布局
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("远程文件"))
        file_layout.addWidget(self.remote_files)
        file_layout.addWidget(QLabel("本地文件"))
        file_layout.addWidget(self.local_files)
        main_layout.addLayout(file_layout)

        # 按钮布局
        button_layout = QHBoxLayout()
        connect_btn = QPushButton("连接 WebDAV", self)
        connect_btn.clicked.connect(self.connect_webdav)
        sync_btn = QPushButton("同步文件", self)
        sync_btn.clicked.connect(self.sync_files)
        start_auto_sync_btn = QPushButton("启动自动同步", self)
        start_auto_sync_btn.clicked.connect(self.start_auto_sync)
        stop_auto_sync_btn = QPushButton("停止自动同步", self)
        stop_auto_sync_btn.clicked.connect(self.stop_auto_sync)
        button_layout.addWidget(connect_btn)
        button_layout.addWidget(sync_btn)
        button_layout.addWidget(start_auto_sync_btn)
        button_layout.addWidget(stop_auto_sync_btn)
        main_layout.addLayout(button_layout)

        # 日志布局
        main_layout.addWidget(QLabel("日志:"))
        main_layout.addWidget(self.log_area)

        # 设置主窗口布局
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def log(self, message):
        """记录日志"""
        self.log_area.append(message)

    def select_local_directory(self):
        """选择本地目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择本地目录")
        if dir_path:
            self.local_dir.setText(dir_path)

            self.local_files.clear()  # 清空列表
            try:
                # 遍历目录中的所有文件
                for filename in os.listdir(dir_path):
                    file_path = os.path.join(dir_path, filename)
                    if os.path.isfile(file_path):  # 仅加载文件，忽略文件夹
                        self.local_files.addItem(filename)
            except Exception as e:
                print(f"加载文件失败: {e}")

    def connect_webdav(self):
        """连接 WebDAV"""
        url = self.webdav_url.text().strip()
        username = self.webdav_username.text().strip()
        password = self.webdav_password.text().strip()

        if not url or not username or not password:
            QMessageBox.warning(self, "错误", "请填写完整的 WebDAV 配置")
            return

        try:
            self.client = Client({
                "webdav_hostname": url,
                "webdav_login": username,
                "webdav_password": password,
            })
            self.log("成功连接到 WebDAV 服务器")
            self.load_remote_files()
        except Exception as e:
            self.log(f"连接 WebDAV 失败: {str(e)}")
            QMessageBox.critical(self, "错误", "无法连接到 WebDAV 服务器")

    def load_remote_files(self):
        """加载远程文件列表"""
        try:
            self.remote_files.clear()
            files = self.client.list("/")
            for file in files:
                self.remote_files.addItem(file)
            self.log("远程文件列表加载完成")
        except Exception as e:
            self.log(f"加载远程文件列表失败: {str(e)}")

    def sync_files(self):
        """同步文件"""
        local_dir = self.local_dir.text().strip()
        if not os.path.exists(local_dir):
            QMessageBox.warning(self, "错误", "本地目录不存在")
            return

        if not self.client:
            QMessageBox.warning(self, "错误", "请先连接 WebDAV 服务器")
            return

        try:
            # 下载远程文件
            for file in self.client.list("/"):
                local_file_path = os.path.join(local_dir, file)
                if not os.path.exists(local_file_path):
                    try:

                        with open(local_file_path, "wb") as f:
                            self.client.download_sync(remote_path=f"/{file}", local_path=local_file_path)
                        self.log(f"下载文件: {file}")
                    except Exception as e:
                        self.log(f"下载文件失败: {file}, 错误信息: {str(e)}")

            # 上传本地文件
            for file in os.listdir(local_dir):
                remote_file_path = f"/{file}"
                try:
                    with open(os.path.join(local_dir, file), "rb") as f:
                        self.client.upload_sync(remote_path=remote_file_path, local_path=f.name)
                    self.log(f"上传文件: {file}")
                except Exception as e:
                    self.log(f"上传文件失败: {file}, 错误信息: {str(e)}")

            self.log("文件同步完成")
        except Exception as e:
            self.log(f"文件同步失败: {str(e)}")

    def start_auto_sync(self):
        """启动自动同步"""
        self.sync_timer.start()
        self.log("自动同步已启动")

    def stop_auto_sync(self):
        """停止自动同步"""
        self.sync_timer.stop()
        self.log("自动同步已停止")


if __name__ == "__main__":
    app = QApplication([])
    window = WebDavSyncTool()
    window.show()
    app.exec()

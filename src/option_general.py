from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication, QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QMessageBox, QCheckBox, QSlider
)
from PySide6.QtGui import QIcon
import os
import sys
import subprocess

from src.const.fs_constants import FsConstants
from src.util.common_util import CommonUtil
from src.util.config_util import ConfigUtil
from src.util.message_util import MessageUtil
from src.widget.menu_window_widget import MenuWindowWidget
from src.widget.transparent_textbox_widget import TransparentTextBox


class OptionGeneral(MenuWindowWidget):

    def __init__(self):
        super().__init__()
        self.slider_value = FsConstants.APP_MINI_SIZE

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("首选项")
        self.setFixedWidth(600)
        #self.setMinimumHeight(400)
        self.setWindowIcon(QIcon(CommonUtil.get_ico_full_path()))
        # 主布局
        main_layout = QVBoxLayout()

        # 高级设置组
        main_layout.addWidget(self.create_advanced_group())

        # 配置文件路径组
        main_layout.addWidget(self.create_config_group())

        # 保存按钮
        save_button_layout = QHBoxLayout()
        save_button_layout.addStretch()
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save_settings)
        save_button_layout.addWidget(save_button)
        main_layout.addLayout(save_button_layout)
        main_layout.addWidget(TransparentTextBox())

        self.setLayout(main_layout)

    def create_advanced_group(self):
        """创建高级设置组"""
        group_box = QGroupBox("高级设置")
        layout = QVBoxLayout()

        # 遮罩动画复选框
        self.mask_checkbox = QCheckBox("遮罩动画")
        layout.addWidget(self.mask_checkbox)
        self.mask_checkbox.setChecked(ConfigUtil.get_ini_mini_mask_checked())

        # 悬浮球设置
        self.float_ball_checkbox = QCheckBox("设置悬浮球")
        self.float_ball_checkbox.stateChanged.connect(self.toggle_visibility)
        layout.addWidget(self.float_ball_checkbox)

        self.float_ball_hide_widget = self.create_float_ball_widget()
        layout.addWidget(self.float_ball_hide_widget)

        if ConfigUtil.get_ini_mini_checked():
            self.float_ball_checkbox.setChecked(True)
            self.slider.setValue(ConfigUtil.get_ini_mini_size())
            self.float_ball_path_input.setText(ConfigUtil.get_ini_mini_image())

        # 托盘图标设置
        self.tray_menu_checkbox = QCheckBox("设置托盘图标")
        self.tray_menu_checkbox.stateChanged.connect(self.tray_menu_visibility)
        layout.addWidget(self.tray_menu_checkbox)

        self.tray_menu_widget = self.create_tray_menu_widget()
        layout.addWidget(self.tray_menu_widget)
        if ConfigUtil.get_ini_tray_menu_checked():
            self.tray_menu_checkbox.setChecked(True)
            self.tray_menu_path_input.setText(ConfigUtil.get_ini_tray_menu_image())

        group_box.setLayout(layout)
        return group_box

    def create_float_ball_widget(self):
        """创建悬浮球相关控件"""
        widget = QWidget()
        layout = QVBoxLayout()

        # 滑块与标签
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(80, 150)
        self.slider.valueChanged.connect(self.update_slider)
        self.slider_label = QLabel("悬浮球大小: 80")
        layout.addWidget(self.slider_label)
        layout.addWidget(self.slider)

        # 文件路径与选择按钮
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("悬浮球图片:"))
        self.float_ball_path_input = QLineEdit()
        self.float_ball_path_input.setReadOnly(True)
        browse_button = QPushButton("选择")
        browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(self.float_ball_path_input)
        file_layout.addWidget(browse_button)
        layout.addLayout(file_layout)

        widget.setLayout(layout)
        widget.setVisible(False)
        return widget

    def create_tray_menu_widget(self):
        """创建托盘图标相关控件"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(QLabel("托盘图标:"))
        self.tray_menu_path_input = QLineEdit()
        self.tray_menu_path_input.setReadOnly(True)
        browse_button = QPushButton("选择")
        browse_button.setObjectName("tray_browse_button")
        browse_button.clicked.connect(self.browse_file)
        layout.addWidget(self.tray_menu_path_input)
        layout.addWidget(browse_button)
        widget.setLayout(layout)
        widget.setVisible(False)
        return widget

    def create_config_group(self):
        """创建配置文件路径组"""
        group_box = QGroupBox("配置文件存储位置")
        layout = QVBoxLayout()

        # 文件路径输入框
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("路径:"))
        self.path_input = QLineEdit()
        self.path_input.setText(os.path.join(CommonUtil.get_external_path(), FsConstants.EXTERNAL_APP_INI_FILE))
        self.path_input.setReadOnly(True)
        input_layout.addWidget(self.path_input)
        layout.addLayout(input_layout)

        # 操作按钮
        button_layout = QHBoxLayout()
        open_dir_button = QPushButton("打开文件所在目录")
        open_dir_button.clicked.connect(self.open_directory)
        open_file_button = QPushButton("打开文件")
        open_file_button.clicked.connect(self.open_file)
        button_layout.addWidget(open_dir_button)
        button_layout.addWidget(open_file_button)
        layout.addLayout(button_layout)

        group_box.setLayout(layout)
        return group_box

    def toggle_visibility(self, state):
        self.float_ball_hide_widget.setVisible(state == Qt.CheckState.Checked.value)

    def tray_menu_visibility(self, state):
        self.tray_menu_widget.setVisible(state == Qt.CheckState.Checked.value)

    def update_slider(self, value):
        self.slider_label.setText(f"悬浮球大小: {value}")
        self.slider_value = value

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "所有文件 (*.png)")
        if file_path:
            sender = self.sender()
            if sender.objectName() == "tray_browse_button":
                self.tray_menu_path_input.setText(file_path)
            else:
                self.float_ball_path_input.setText(file_path)


    def open_directory(self):
        """打开文件所在目录"""
        file_path = self.path_input.text().strip()
        if not file_path or not os.path.exists(file_path):
            MessageUtil.show_success_message("请输入有效的文件路径！")
            return

        # 获取目录路径
        dir_path = os.path.dirname(file_path)
        try:
            if CommonUtil.check_win_os():
                subprocess.Popen(f'explorer "{dir_path}"')
            elif CommonUtil.check_mac_os():
                subprocess.Popen(["open", dir_path])
            else:
                subprocess.Popen(["xdg-open", dir_path])
        except Exception as e:
            MessageUtil.show_error_message(f"无法打开目录: {e}")

    def open_file(self):
        """打开文件"""
        file_path = self.path_input.text().strip()
        if not file_path or not os.path.isfile(file_path):
            MessageUtil.show_warning_message("请输入有效的文件路径！")
            return

        try:
            if CommonUtil.check_win_os():
                os.startfile(file_path)
            elif CommonUtil.check_mac_os():
                subprocess.Popen(["open", file_path])
            else:
                subprocess.Popen(["xdg-open", file_path])
        except Exception as e:
            MessageUtil.show_error_message(f"无法打开目录: {e}")

    def save_settings(self):
        """保存设置"""
        if self.float_ball_checkbox.isChecked() and not self.float_ball_path_input.text().strip():
            MessageUtil.show_warning_message("请为悬浮球选择图片！")
            return

        if self.tray_menu_checkbox.isChecked() and not self.tray_menu_path_input.text().strip():
            MessageUtil.show_warning_message("请为托盘图标选择图片！")
            return
        """保存设置到 ini 文件"""

        mask_enabled = self.mask_checkbox.isChecked()
        mini_enabled = self.float_ball_checkbox.isChecked()
        tray_menu_enabled = self.tray_menu_checkbox.isChecked()
        try:
            ConfigUtil.set_ini_mini_mask_checked(mask_enabled)
            ConfigUtil.set_ini_mini_checked(mini_enabled)  # 将 悬浮球修改状态写入到配置文件
            ConfigUtil.set_ini_tray_menu_checked(tray_menu_enabled)  # 将 托盘图标修改的状态写入到配置文件
            if mini_enabled:
                ConfigUtil.set_ini_mini_size(self.slider_value)
                ConfigUtil.set_ini_mini_image(self.float_ball_path_input.text().strip())
            if tray_menu_enabled:
                ConfigUtil.set_ini_tray_menu_image(self.tray_menu_path_input.text().strip())
            MessageUtil.show_success_message("设置已成功保存！")
        except Exception as e:
            MessageUtil.show_error_message(f"保存设置失败: {e}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OptionGeneral()
    window.show()
    sys.exit(app.exec())

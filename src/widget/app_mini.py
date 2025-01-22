import random

from PySide6.QtCore import QPropertyAnimation, QPoint
from PySide6.QtCore import QTimer
from PySide6.QtCore import Qt, QEasingCurve
from PySide6.QtGui import QMouseEvent, QPixmap, QGuiApplication
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from loguru import logger

from src.const.fs_constants import FsConstants
from src.util.common_util import CommonUtil
from src.util.config_util import ConfigUtil


class FloatingBall(QWidget):

    def __init__(self, main_window):
        super().__init__()
        # 清除外部QSS影响
        self.setStyleSheet("background-color: transparent;")
        self.main_window = main_window
        self.init_ui()



    def init_ui(self):
        logger.info("---- 悬浮球初始化 ----")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        app_mini_size = ConfigUtil.get_ini_mini_size()
        self.setGeometry(0, 0, app_mini_size, app_mini_size)  # 设置悬浮球大小
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)  # 设置窗口背景透明

        #self.setWindowOpacity(0.8)  # 设置透明度

        self.setup_background_image()
        self.move_to_top_right()

        self.dragPosition = None
        self.setMouseTracking(True)



        # 启动呼吸灯效果（透明度周期性变化）
        #self.breathing_light_window()
        # 悬浮球的缓慢漂浮（上下浮动）
        self.add_float_animation()
        if ConfigUtil.get_ini_mini_mask_checked():
            self.add_mask_animation()
            self.add_mask_breathing_effect()
        # 随机跑
        #self.add_random_walk()

    # ------ 启动呼吸灯效果（透明度周期性变化）[START]
    def breathing_light_window(self):
        logger.info("---- 悬浮球启动呼吸灯效果 ----")
        # 初始透明度
        self.opacity = 0.2
        # 透明度每次变化的值，控制呼吸的速度和节奏
        self.direction = 0.02
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_opacity)
        # 设置定时器间隔为50毫秒，可根据需要调整呼吸节奏快慢
        self.timer.start(50)

    # 更新透明度
    def update_opacity(self):
        self.opacity += self.direction
        if self.opacity >= 1.0:
            self.direction = -0.02  # 达到最大透明度后开始减小透明度
        elif self.opacity <= 0.2:
            self.direction = 0.02  # 达到最小透明度后开始增大透明度
        self.setWindowOpacity(self.opacity)
    # ------ 启动呼吸灯效果（透明度周期性变化）[END]


    # ---------悬浮球的缓慢漂浮（上下浮动）[START]
    def add_float_animation(self):
        # 创建属性动画，调整窗口位置
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(2000)  # 动画时长2秒
        self.animation.setStartValue(self.pos())  # 初始位置
        self.animation.setKeyValueAt(0.5, self.pos() + QPoint(0, 10))  # 浮动到10像素下方
        self.animation.setEndValue(self.pos())  # 回到原位置
        self.animation.setLoopCount(-1)  # 无限循环
        self.animation.setEasingCurve(QEasingCurve.Type.InOutSine)  # 平滑效果
        self.animation.start()

    def update_animation_start_position(self):
        if hasattr(self, "animation"):
            # 停止当前动画
            self.animation.stop()

            # 更新动画起始位置为当前窗口位置
            self.animation.setStartValue(self.pos())

            # 更新动画结束位置（基于当前窗口位置计算浮动范围）
            self.animation.setKeyValueAt(0.5, self.pos() + QPoint(0, 10))  # 下浮10像素
            self.animation.setEndValue(self.pos())  # 回到原位置
            self.animation.start()
    # ---------悬浮球的缓慢漂浮（上下浮动）[END]

    # -------- 随机出现位置 【START】
    def add_random_walk(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.random_move)
        self.timer.start(1000)  # 每秒移动一次

    def random_move(self):
        screen_geo = QGuiApplication.primaryScreen().geometry()
        new_x = random.randint(0, screen_geo.width() - self.width())
        new_y = random.randint(0, screen_geo.height() - self.height())
        self.move(new_x, new_y)
    # -------- 随机出现位置 【END】


    # ------ 添加遮罩 [START]
    def add_mask(self):
        self.mask = QLabel(self)
        self.mask.setStyleSheet("background-color: rgba(0, 0, 0, 30%); border-radius: 10px;")
        self.mask.resize(self.size())
        # 偏移位置调整
        offset_x = 15  # 向右偏移5像素
        offset_y = 15  # 向下偏移5像素
        self.mask.move(offset_x, offset_y)
        self.mask.lower()  # 遮罩放在背景图的下层

    # -------遮罩动态缩放（呼吸效果）
    def add_mask_breathing_effect(self):
        self.breathing_animation = QPropertyAnimation(self.mask, b"size")
        self.breathing_animation.setDuration(4000)
        # 设置动画初始大小（从大到小）
        self.breathing_animation.setStartValue(self.mask.size())  # 当前大小
        self.breathing_animation.setEndValue(self.mask.size() * 0.8)  # 缩小到80%

        # 设置动画的关键帧：由小到大
        self.breathing_animation.setKeyValueAt(0.5, self.mask.size() * 0.8)  # 在50%位置达到最小值
        self.breathing_animation.setKeyValueAt(1.0, self.mask.size())  # 在100%位置回到原始大小

        self.breathing_animation.setLoopCount(-1)
        # 设置动画的缓动曲线（InOutSine 曲线会让动画更平滑）
        self.breathing_animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.breathing_animation.start()

    # ------ 实现动态遮罩（移动效果）
    def add_mask_animation(self):
        self.mask_animation = QPropertyAnimation(self.mask, b"pos")
        self.mask_animation.setDuration(2000)  # 动画时长
        self.mask_animation.setStartValue(self.mask.pos())  # 初始位置
        self.mask_animation.setKeyValueAt(0.5, self.mask.pos() + QPoint(0, 10))  # 向下偏移10像素
        self.mask_animation.setEndValue(self.mask.pos())  # 回到初始位置
        self.mask_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)  # 平滑效果
        self.mask_animation.setLoopCount(-1)  # 无限循环
        self.mask_animation.start()

    # ------ 设置悬浮球背景
    def setup_background_image(self):
        logger.info("---- 初始化悬浮球背景图 ----")
        layout = QVBoxLayout()
        # 这里使用一个示例图片路径，你可以替换为真实路径
        pixmap = QPixmap(ConfigUtil.get_ini_mini_image())
        pixmap = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.background_label = QLabel(self)
        self.background_label.setPixmap(pixmap)
        self.background_label.resize(self.size())
        layout.addWidget(self.background_label)
        self.setLayout(layout)
        # 添加遮罩
        if ConfigUtil.get_ini_mini_mask_checked():
            self.add_mask()




    def move_to_top_right(self):
        logger.info("---- 初始化悬浮球位置 ----")
        screen_geo = QGuiApplication.primaryScreen().geometry()
        x = screen_geo.width() - self.width() - 10
        y = 10
        self.move(x, y)

    # 鼠标按下事件
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            # 暂停动画
            if hasattr(self, "animation") and self.animation.state() == QPropertyAnimation.State.Running:
                self.animation.pause()

            # 保存鼠标相对窗口左上角的位置
            self.dragPosition = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    # 鼠标移动事件
    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton and self.dragPosition:
            self.move(event.globalPosition().toPoint() - self.dragPosition)
            event.accept()

    # 鼠标释放
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:

            # 更新动画的位置
            if hasattr(self, "animation"):
                self.update_animation_start_position()

            # 鼠标释放后恢复动画
            if hasattr(self, "animation") and self.animation.state() == QPropertyAnimation.State.Paused:
                self.animation.resume()
            self.dragPosition = None
            event.accept()

    def show_main_window(self):
        logger.info("---- 双击悬浮球，打开主界面 ----")
        self.main_window.show()
        self.main_window.is_floating_ball_visible = False
        self.hide()

    # 鼠标双击，打开主界面
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.show_main_window()



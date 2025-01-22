class FsConstants:
    """
    ---------------------
    宽度为0 高度为0,则表示窗口【宽高】由组件们决定
    ---------------------
    """
    # 主窗口相关常量
    APP_WINDOW_WIDTH = 300
    APP_WINDOW_HEIGHT = 300
    APP_WINDOW_TITLE = "FSDiary"
    VERSION = "0.1.0"
    COPYRIGHT_INFO = f"© 2025 {APP_WINDOW_TITLE}"
    # 悬浮球相关常量
    APP_MINI_SIZE = 80
    APP_MINI_WINDOW_TITLE = ""

    # 工具栏相关常量
    TOOLBAR_HELP_TITLE = "帮助"
    TOOLBAR_README_TITLE = "说明"
    TOOLBAR_AUTHOR_TITLE = "作者"

    WINDOW_TITLE_IMAGE_TOOL = "图片工具"


    # 共用的常量，应用图标
    APP_ICON_FULL_PATH = "resources/images/app.ico"
    APP_MINI_ICON_FULL_PATH = "resources/images/app_mini.ico"
    APP_BAR_ICON_FULL_PATH = "resources/images/app_bar.ico"
    UPLOAD_IMAGE_FULL_PATH = "resources/images/upload.svg"
    AUTHOR_MAIL = "xueyao.me@gmail.com"
    AUTHOR_BLOG = "https://blog.xueyao.tech"
    AUTHOR_GITHUB = "https://github.com/flowstone"
    PROJECT_ADDRESS = "https://github.com/flowstone/FSDiary"
    BASE_QSS_PATH = "resources/qss/base.qss"
    LICENSE_FILE_PATH = "resources/txt/LICENSE"


    EDIT_BTN_PATH = "resources/btn/edit-btn.svg"
    MARKDOWN_BTN_PATH = "resources/btn/markdown-btn.svg"
    NEW_DIARY_BTN_PATH = "resources/btn/new-diary-btn.svg"




    # 保存文件路径
    SAVE_FILE_PATH_WIN = "C:\\FSDiary\\"
    SAVE_FILE_PATH_MAC = "~/FSDiary/"
    EXTERNAL_APP_INI_FILE = "app.ini"

    APP_INI_FILE = "app.ini"
    HELP_PDF_FILE_PATH = "resources/pdf/help.pdf"
    FONT_FILE_PATH = "resources/fonts/AlimamaFangYuanTiVF-Thin.ttf"

    DIARY_ENC_PATH = "diaries"
    DIARY_KEY_PATH = "secret.key"

    #首选项
    PREFERENCES_WINDOW_TITLE = "首选项"
    PREFERENCES_WINDOW_TITLE_ABOUT = "关于"
    PREFERENCES_WINDOW_TITLE_GENERAL = "常规"

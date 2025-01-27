from fs_base.const import AppConstants


class FsConstants(AppConstants):
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

    UPLOAD_IMAGE_FULL_PATH = "resources/images/upload.svg"
    BASE_QSS_PATH = "resources/qss/base.qss"
    LICENSE_FILE_PATH = "resources/txt/LICENSE"


    EDIT_BTN_PATH = "resources/images/btn/edit-btn.svg"
    MARKDOWN_BTN_PATH = "resources/images/btn/markdown-btn.svg"
    NEW_DIARY_BTN_PATH = "resources/images/btn/new-diary-btn.svg"

    BOLD_ICON_PATH = "resources/images/icon/bold.svg"
    ITALIC_ICON_PATH = "resources/images/icon/italic.svg"
    PEN_LINE_ICON_PATH = "resources/images/icon/pen-line.svg"
    LINK_ICON_PATH = "resources/images/icon/link.svg"
    IMAGE_ICON_PATH = "resources/images/icon/image.svg"
    COLOR_ICON_PATH = "resources/images/icon/font-colors.svg"
    HR_ICON_PATH = "resources/images/icon/hr.svg"
    BLOCKQUOTE_ICON_PATH = "resources/images/icon/blockquote.svg"
    TABLE_ICON_PATH = "resources/images/icon/table.svg"
    H1_ICON_PATH = "resources/images/icon/h1.svg"
    H2_ICON_PATH = "resources/images/icon/h2.svg"
    H3_ICON_PATH = "resources/images/icon/h3.svg"
    UNORDERED_LIST_ICON_PATH = "resources/images/icon/unordered-list.svg"
    ORDERED_LIST_ICON_PATH = "resources/images/icon/ordered-list.svg"
    CHECKBOX_LIST_ICON_PATH = "resources/images/icon/checkbox-list.svg"
    TIMESTAMP_ICON_PATH = "resources/images/icon/time.svg"

    FILE_REMOVE_RIGHT_MENU_PATH = "resources/images/menu/file-remove.svg"
    FILE_RENAME_RIGHT_MENU_PATH = "resources/images/menu/file-rename.svg"
    FOLDER_ADD_RIGHT_MENU_PATH = "resources/images/menu/folder-add.svg"
    FOLDER_RENAME_RIGHT_MENU_PATH = "resources/images/menu/folder_rename.svg"
    PDF_RIGHT_MENU_PATH = "resources/images/menu/pdf.svg"

    DIARY_TREE_ICON_PATH = "resources/images/icon/diary-tree.svg"
    FOLDER_TREE_ICON_PATH = "resources/images/icon/folder-tree.svg"
    ROOT_FOLDER_TREE_ICON_PATH = "resources/images/icon/root-folder.svg"


    # 保存文件路径
    SAVE_FILE_PATH_WIN = "C:\\FSDiary\\"
    SAVE_FILE_PATH_MAC = "~/FSDiary/"
    EXTERNAL_APP_INI_FILE = "app.ini"

    APP_INI_FILE = "app.ini"
    HELP_PDF_FILE_PATH = "resources/pdf/help.pdf"
    FONT_FILE_PATH = "resources/fonts/AlimamaFangYuanTiVF-Thin.ttf"

    DIARY_ENC_PATH = "diaries"
    DIARY_ARTICLE_PATH = "diaries/Diary"
    DIARY_KEY_PATH = "secret.key"

    #首选项
    PREFERENCES_WINDOW_TITLE = "首选项"
    PREFERENCES_WINDOW_TITLE_ABOUT = "关于"
    PREFERENCES_WINDOW_TITLE_GENERAL = "常规"



 # INI 文件配置节名称
    SETTINGS_SECTION = "Settings"

    # 配置键名

    WEBDAV_AUTO_CHECKED_KEY = "webdav.auto.checked"
    WEBDAV_ADDRESS_KEY = "webdav.address"
    WEBDAV_USERNAME_KEY = "webdav.username"
    WEBDAV_PASSWORD_KEY = "webdav.password"
    WEBDAV_LOCAL_DIR_KEY = "webdav.local.dir"
    WEBDAV_REMOTE_DIR_KEY = "webdav.remote.dir"

    # 默认值
    NEW_CONFIG = {
        WEBDAV_AUTO_CHECKED_KEY: False,
        WEBDAV_ADDRESS_KEY: "",
        WEBDAV_USERNAME_KEY: "",
        WEBDAV_PASSWORD_KEY: "",
        WEBDAV_LOCAL_DIR_KEY: "",
        WEBDAV_REMOTE_DIR_KEY: "",
    }

    DEFAULT_CONFIG = {**AppConstants.DEFAULT_CONFIG, **NEW_CONFIG}

    # 类型映射
    NEW_CONFIG_TYPES = {
        WEBDAV_AUTO_CHECKED_KEY: bool,
        WEBDAV_ADDRESS_KEY: str,
        WEBDAV_USERNAME_KEY: str,
        WEBDAV_PASSWORD_KEY: str,
        WEBDAV_LOCAL_DIR_KEY: str,
        WEBDAV_REMOTE_DIR_KEY: str,
    }
    CONFIG_TYPES = {**AppConstants.CONFIG_TYPES, **NEW_CONFIG_TYPES}
    ################### INI设置 #####################

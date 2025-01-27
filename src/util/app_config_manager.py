from fs_base import ConfigManager
from src.const.fs_constants import FsConstants


class AppConfigManager(ConfigManager):
    def __init__(self):
        super().__init__()
        self.default_config = FsConstants.DEFAULT_CONFIG  # 使用扩展后的配置

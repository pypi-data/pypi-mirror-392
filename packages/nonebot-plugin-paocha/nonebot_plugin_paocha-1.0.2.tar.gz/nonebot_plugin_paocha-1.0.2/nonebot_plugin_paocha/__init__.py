# nonebot_plugin_paocha/__init__.py
from .main import __plugin_meta__, sign, sign_info, grade, help_cmd, user_mapping, clear_mapping, user_list, search_user, delete_user, upload_image, image_stats

__all__ = [
    "__plugin_meta__", 
    "sign", "sign_info", "grade", "help_cmd", 
    "user_mapping", "clear_mapping", "user_list", 
    "search_user", "delete_user", "upload_image", "image_stats"
]

__version__ = "1.0.2"
import typing

script_folder = "javascript"
script_names: typing.List[str] = [
    "utils.js",
    "iframe_content_window.js",
    "navigator_user_agent.js",
    "chrome_app.js",
    "media_codecs.js",
    "navigator_vendor.js",
    "chrome_csi.js",
    "navigator_hardware_concurrency.js",
    "navigator_webdriver.js",
    "chrome_hairline.js",
    "navigator_languages.js",
    "web_gl_vendor.js",
    "chrome_load_times.js",
    "navigator_permissions.js",
    "window_outer_dimensions.js",
    "chrome_runtime.js",
    "navigator_platform.js",
    "generate_magic_arrays.js",
    "navigator_plugins.js",
]

browser_options: typing.Dict[str, typing.Any] = {}
context_options: typing.Dict[str, typing.Any] = {}

import os
import sys

sys.__file__ = os.path.abspath(__file__)

from playwright_stealth_plugin.python import async_api, sync_api

__all__ = ["async_api", "sync_api"]
# [line-length: 150]

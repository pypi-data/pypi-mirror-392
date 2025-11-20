import typing

script_folder = "_javascript"
script_names: typing.List[str] = [
    "utils.js",
    "chrome.app.js",
    "chrome.csi.js",
    "chrome.hairline.js",
    "chrome.load.times.js",
    "chrome.runtime.js",
    "generate.magic.arrays.js",
    "iframe.contentWindow.js",
    "media.codecs.js",
    "navigator.hardwareConcurrency.js",
    "navigator.languages.js",
    "navigator.permissions.js",
    "navigator.platform.js",
    "navigator.plugins.js",
    "navigator.userAgent.js",
    "navigator.vendor.js",
    "navigator.webdriver.js",
    "webgl.vendor.js",
    "window.outerdimensions.js",
]

browser_options: typing.Dict[str, typing.Any] = {}
context_options: typing.Dict[str, typing.Any] = {}

import os
import sys
import playwright_stealth_plugin

sys.__file__ = os.path.abspath(playwright_stealth_plugin.__file__)

# [line-length: 150]

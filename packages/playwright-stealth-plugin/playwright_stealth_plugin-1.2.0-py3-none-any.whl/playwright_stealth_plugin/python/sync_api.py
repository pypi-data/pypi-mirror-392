import os
import sys
import typing

import playwright.sync_api
import playwright_stealth_plugin

browser_options = playwright_stealth_plugin.browser_options
context_options = playwright_stealth_plugin.context_options

original_launch: typing.Callable[..., playwright.sync_api.Browser]
original_new_context: typing.Callable[..., playwright.sync_api.BrowserContext]
original_launch_persistent_context: typing.Callable[..., playwright.sync_api.BrowserContext]


def plugin_code(context: playwright.sync_api.BrowserContext):
    for script_name in playwright_stealth_plugin.script_names:
        relative_path = os.path.join(os.path.dirname(sys.__file__), playwright_stealth_plugin.script_folder, script_name)
        absolute_path = os.path.abspath(relative_path)
        with open(absolute_path, mode="r", encoding="utf-8") as script_file:
            script_content = script_file.read()
            context.add_init_script(script_content)


def custom_launch(self: playwright.sync_api.BrowserType, *args: typing.Any, **kwargs: typing.Any):
    browser = original_launch(self, *args, **browser_options, **kwargs)
    global original_new_context
    original_new_context = type(browser).new_context
    type(browser).new_context = custom_new_context
    return browser


def custom_new_context(self: playwright.sync_api.Browser, *args: typing.Any, **kwargs: typing.Any):
    context = original_new_context(self, *args, **context_options, **kwargs)
    plugin_code(context)
    return context


def custom_launch_persistent_context(self: playwright.sync_api.BrowserType, *args: typing.Any, **kwargs: typing.Any):
    context = original_launch_persistent_context(self, *args, **browser_options, **context_options, **kwargs)
    plugin_code(context)
    return context


def apply(playwright: playwright.sync_api.Playwright):
    global original_launch, original_launch_persistent_context
    original_launch = type(playwright.chromium).launch
    original_launch_persistent_context = type(playwright.chromium).launch_persistent_context

    type(playwright.chromium).launch = custom_launch
    type(playwright.chromium).launch_persistent_context = custom_launch_persistent_context


__all__ = ["apply"]
# [line-length: 150]

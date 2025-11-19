import re
import sys
import json
import typing
import asyncio

import playwright.sync_api
import playwright.async_api
import playwright_stealth_plugin.evasions.python._utils as utils
import playwright_stealth_plugin.evasions.python.chrome_app
import playwright_stealth_plugin.evasions.python.chrome_csi
import playwright_stealth_plugin.evasions.python.chrome_hairline
import playwright_stealth_plugin.evasions.python.chrome_load_times
import playwright_stealth_plugin.evasions.python.chrome_runtime
import playwright_stealth_plugin.evasions.python.generate_magic_arrays
import playwright_stealth_plugin.evasions.python.iframe_content_window
import playwright_stealth_plugin.evasions.python.media_codecs
import playwright_stealth_plugin.evasions.python.navigator_hardware_concurrency
import playwright_stealth_plugin.evasions.python.navigator_languages
import playwright_stealth_plugin.evasions.python.navigator_permissions
import playwright_stealth_plugin.evasions.python.navigator_platform
import playwright_stealth_plugin.evasions.python.navigator_plugins
import playwright_stealth_plugin.evasions.python.navigator_user_agent
import playwright_stealth_plugin.evasions.python.navigator_vendor
import playwright_stealth_plugin.evasions.python.navigator_webdriver
import playwright_stealth_plugin.evasions.python.web_gl_vendor
import playwright_stealth_plugin.evasions.python.window_outer_dimensions


# plugin_code
async def async_plugin_code(context: playwright.async_api.BrowserContext):
    for variable_name, variable_value in utils.variables.items():
        script = f"window.{variable_name} = {json.dumps(variable_value)};"
        await context.add_init_script(script)
    for script in utils.scripts:
        await context.add_init_script(script)


def sync_plugin_code(context: playwright.sync_api.BrowserContext):
    for variable_name, variable_value in utils.variables.items():
        script = f"window.{variable_name} = {json.dumps(variable_value)};"
        context.add_init_script(script)
    for script in utils.scripts:
        context.add_init_script(script)


# custom_launch
async def async_custom_launch(self, *args: typing.Any, **kwargs: typing.Any) -> playwright.async_api.Browser:
    browser: playwright.async_api.Browser = await async_original_launch(
        self,
        *args,
        **utils.options["browser"],
        **kwargs,
    )
    global async_original_new_context
    async_original_new_context = type(browser).new_context
    type(browser).new_context = async_custom_new_context
    return browser


def sync_custom_launch(self, *args: typing.Any, **kwargs: typing.Any) -> playwright.sync_api.Browser:
    browser: playwright.sync_api.Browser = sync_original_launch(
        self,
        *args,
        **utils.options["browser"],
        **kwargs,
    )
    global sync_original_new_context
    sync_original_new_context = type(browser).new_context
    type(browser).new_context = sync_custom_new_context
    return browser


# custom_new_context
async def async_custom_new_context(self, *args: typing.Any, **kwargs: typing.Any) -> playwright.async_api.BrowserContext:
    context: playwright.async_api.BrowserContext = await async_original_new_context(
        self,
        *args,
        **utils.options["context"],
        **kwargs,
    )
    await async_plugin_code(context)
    return context


def sync_custom_new_context(self, *args: typing.Any, **kwargs: typing.Any) -> playwright.sync_api.BrowserContext:
    context: playwright.sync_api.BrowserContext = sync_original_new_context(
        self,
        *args,
        **utils.options["context"],
        **kwargs,
    )
    sync_plugin_code(context)
    return context


# custom_launch_persistent_context
async def async_custom_launch_persistent_context(self, *args: typing.Any, **kwargs: typing.Any) -> playwright.async_api.BrowserContext:
    context: playwright.async_api.BrowserContext = await async_original_launch_persistent_context(
        self,
        *args,
        **utils.options["browser"],
        **utils.options["context"],
        **kwargs,
    )
    await async_plugin_code(context)
    return context


def sync_custom_launch_persistent_context(self, *args: typing.Any, **kwargs: typing.Any) -> playwright.sync_api.BrowserContext:
    context: playwright.sync_api.BrowserContext = sync_original_launch_persistent_context(
        self,
        *args,
        **utils.options["browser"],
        **utils.options["context"],
        **kwargs,
    )
    sync_plugin_code(context)
    return context


# run_all
async def async_run_all() -> None:
    for name, module in sys.modules.items():
        if re.match(r"playwright_stealth_plugin\.evasions\.python\.(.+)", name):
            module.run()


def sync_run_all() -> None:
    for name, module in sys.modules.items():
        if re.match(r"playwright_stealth_plugin\.evasions\.python\.(.+)", name):
            module.run()


# apply
async def async_apply(playwright: playwright.async_api.Playwright):
    await async_run_all()

    global async_original_launch, async_original_launch_persistent_context
    async_original_launch = type(playwright.chromium).launch
    async_original_launch_persistent_context = type(playwright.chromium).launch_persistent_context

    type(playwright.chromium).launch = async_custom_launch
    type(playwright.chromium).launch_persistent_context = async_custom_launch_persistent_context


def sync_apply(playwright: playwright.sync_api.Playwright):
    sync_run_all()

    global sync_original_launch, sync_original_launch_persistent_context
    sync_original_launch = type(playwright.chromium).launch
    sync_original_launch_persistent_context = type(playwright.chromium).launch_persistent_context

    type(playwright.chromium).launch = sync_custom_launch
    type(playwright.chromium).launch_persistent_context = sync_custom_launch_persistent_context


# [line-length : 150]

import re
import sys
import json
import typing

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


async def plugin_code(context: playwright.async_api.BrowserContext):
    for variable_name, variable_value in utils.variables.items():
        script = f"window.{variable_name} = {json.dumps(variable_value)};"
        await context.add_init_script(script)
    for script in utils.scripts:
        await context.add_init_script(script)


async def custom_launch(self, *args: typing.Any, **kwargs: typing.Any) -> playwright.async_api.Browser:
    browser: playwright.async_api.Browser = await original_launch(
        self,
        *args,
        **utils.options["browser"],
        **kwargs,
    )
    global original_new_context
    original_new_context = type(browser).new_context
    type(browser).new_context = custom_new_context
    return browser


async def custom_new_context(self, *args: typing.Any, **kwargs: typing.Any) -> playwright.async_api.BrowserContext:
    context: playwright.async_api.BrowserContext = await original_new_context(
        self,
        *args,
        **utils.options["context"],
        **kwargs,
    )
    await plugin_code(context)
    return context


async def custom_launch_persistent_context(self, *args: typing.Any, **kwargs: typing.Any) -> playwright.async_api.BrowserContext:
    context: playwright.async_api.BrowserContext = await original_launch_persistent_context(
        self,
        *args,
        **utils.options["browser"],
        **utils.options["context"],
        **kwargs,
    )
    await plugin_code(context)
    return context


async def apply(playwright: playwright.async_api.Playwright):
    for name, module in sys.modules.items():
        if re.match(r"playwright_stealth_plugin\.evasions\.python\.(.+)", name):
            await module.run()

    global original_launch, original_launch_persistent_context
    original_launch = type(playwright.chromium).launch
    original_launch_persistent_context = type(playwright.chromium).launch_persistent_context

    type(playwright.chromium).launch = custom_launch
    type(playwright.chromium).launch_persistent_context = custom_launch_persistent_context


# [line-length : 150]

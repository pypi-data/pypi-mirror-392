import playwright_stealth_plugin.evasions.python._utils as _utils


async def run():
    script = _utils.read_script(f"../javascript/{__name__.split(".")[-1]}.js")
    _utils.scripts.append(script)
    _utils.logger.info(f"RUN: {__name__}")


# async beforeLaunch(options) {
#     // Have viewport match window size, unless specified by user
#     // https://github.com/GoogleChrome/puppeteer/issues/3688
#     if (!('defaultViewport' in options)) {
#       options.defaultViewport = null
#     }
#     return options
#   }

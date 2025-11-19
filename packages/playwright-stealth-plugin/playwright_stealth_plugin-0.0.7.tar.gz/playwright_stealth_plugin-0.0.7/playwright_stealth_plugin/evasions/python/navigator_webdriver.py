import playwright_stealth_plugin.evasions.python._utils as _utils


async def run():
    script = _utils.read_script(f"../javascript/{__name__.split(".")[-1]}.js")
    _utils.scripts.append(script)
    _utils.logger.info(f"RUN: {__name__}")


# function beforeLaunch(options) {
#   // If disable-blink-features is already passed, append the AutomationControlled switch
#   const idx = options.args.findIndex((arg) =>
#     arg.startsWith("--disable-blink-features=")
#   );
#   if (idx !== -1) {
#     const arg = options.args[idx];
#     options.args[idx] = `${arg},AutomationControlled`;
#   } else {
#     options.args.push("--disable-blink-features=AutomationControlled");
#   }
# }

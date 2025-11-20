import playwright_stealth_plugin._python.async_api
import playwright_stealth_plugin._python.sync_api

async_apply = playwright_stealth_plugin._python.async_api.apply
sync_apply = playwright_stealth_plugin._python.sync_api.apply
__all__ = ["async_apply", "sync_apply"]

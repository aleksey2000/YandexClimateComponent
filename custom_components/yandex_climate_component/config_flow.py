from copy import deepcopy
import logging
from typing import Any, Dict, Optional

from homeassistant import ConfigEntry, ConfigFlow, config_entries, core
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_NAME, CONF_PATH, CONF_URL
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_registry import (
    async_entries_for_config_entry,
    async_get,
)
import voluptuous as vol

from .const import CONF_REPOS, DOMAIN

_LOGGER = logging.getLogger(__name__)

AUTH_SCHEMA = vol.Schema(
    {vol.Required(CONF_ACCESS_TOKEN): cv.string}
)

class YandexClimateFlowHandler(ConfigFlow, domain=DOMAIN):
    
    async def async_step_import(self, data: dict):
        """Import a config entry."""

    
    async def async_step_user(self, user_input=None):
        """Init by user via GUI"""

        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required("method", default="token"): vol.In(
                            {
                                "auth": "Пароль или одноразовый ключ",
                                "token": "Токен",
                            }
                        )
                    }
                ),
            )
        
        method = user_input["method"]

        if method == "auth":
            return self.async_show_form(
                step_id=method,
                data_schema=vol.Schema(
                    {
                        vol.Required("username"): str,
                        vol.Required("password"): str,
                    }
                ),
            )

        if method == "token":
            return self.async_show_form(
            step_id=method,
            data_schema=vol.Schema(
                {
                    vol.Required(method): str,
                }
            ),
        )

    async def async_step_auth(self, user_input):
        """User submited username and password. Or YAML error."""
        resp = await self.yandex.login_username(user_input["username"])
        if resp.ok:
            resp = await self.yandex.login_password(user_input["password"])
        return await self._check_yandex_response(resp)
    
    async def async_step_token(self, user_input):
        resp = await self.yandex.validate_token(user_input["token"])
        return await self._check_yandex_response(resp)
    
    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        pass
        #return OptionsFlowHandler()

def vol_schema(schema: dict, defaults: dict | None) -> vol.Schema:
    if defaults:
        for key in schema:
            if (value := defaults.get(key.schema)) is not None:
                key.default = vol.default_factory(value)
    return vol.Schema(schema)
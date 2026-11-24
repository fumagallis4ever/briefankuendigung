import imaplib

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    CONF_AUFBEWAHRUNG,
    CONF_SERVER,
    DEFAULT_AUFBEWAHRUNG,
    DEFAULT_SERVER,
    DOMAIN,
)


def _login_test(server: str, benutzer: str, passwort: str) -> None:
    imap = imaplib.IMAP4_SSL(server, 993, timeout=20)
    try:
        imap.login(benutzer, passwort)
    finally:
        try:
            imap.logout()
        except Exception:
            pass


class BriefConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return BriefOptionsFlow()

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_USERNAME].lower())
            self._abort_if_unique_id_configured()
            try:
                await self.hass.async_add_executor_job(
                    _login_test,
                    user_input[CONF_SERVER],
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                )
            except imaplib.IMAP4.error:
                errors["base"] = "invalid_auth"
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME], data=user_input
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_SERVER, default=DEFAULT_SERVER): str,
                vol.Required(CONF_USERNAME): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.EMAIL)
                ),
                vol.Required(CONF_PASSWORD): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.PASSWORD)
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)


class BriefOptionsFlow(config_entries.OptionsFlowWithReload):

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                data={CONF_AUFBEWAHRUNG: int(user_input[CONF_AUFBEWAHRUNG])}
            )
        aktuell = self.config_entry.options.get(CONF_AUFBEWAHRUNG, DEFAULT_AUFBEWAHRUNG)
        schema = vol.Schema(
            {
                vol.Required(CONF_AUFBEWAHRUNG, default=aktuell): NumberSelector(
                    NumberSelectorConfig(
                        min=1, max=365, step=1,
                        mode=NumberSelectorMode.BOX,
                        unit_of_measurement="Tage",
                    )
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)

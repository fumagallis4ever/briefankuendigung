import os

from homeassistant.components.image import ImageEntity
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import BriefCoordinator


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([UmschlagBild(entry.runtime_data, entry)])


def _lesen(pfad: str) -> bytes | None:
    if not os.path.exists(pfad):
        return None
    with open(pfad, "rb") as f:
        return f.read()


class UmschlagBild(CoordinatorEntity[BriefCoordinator], ImageEntity):
    _attr_has_entity_name = True
    _attr_name = "Umschlag"
    _attr_content_type = "image/jpeg"

    def __init__(self, coordinator: BriefCoordinator, entry) -> None:
        super().__init__(coordinator)
        ImageEntity.__init__(self, coordinator.hass)
        self._attr_unique_id = f"{entry.entry_id}_umschlag"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry.entry_id)})
        self._datei = None
        self._datei_pruefen()

    def _datei_pruefen(self) -> None:
        briefe = self.coordinator.data or []
        datei = briefe[-1].get("datei") if briefe else None
        if datei != self._datei:
            self._datei = datei
            self._attr_image_last_updated = dt_util.utcnow()

    @callback
    def _handle_coordinator_update(self) -> None:
        self._datei_pruefen()
        super()._handle_coordinator_update()

    async def async_image(self) -> bytes | None:
        if not self._datei:
            return None
        pfad = os.path.join(self.coordinator.bild_ordner, self._datei)
        return await self.hass.async_add_executor_job(_lesen, pfad)

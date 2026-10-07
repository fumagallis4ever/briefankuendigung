from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BriefCoordinator


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([LetzterBriefSensor(entry.runtime_data, entry)])


class LetzterBriefSensor(CoordinatorEntity[BriefCoordinator], SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Letzter Brief"
    _attr_icon = "mdi:email-outline"

    def __init__(self, coordinator: BriefCoordinator, entry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_letzter_brief"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Briefankündigung",
            manufacturer="Deutsche Post / WEB.DE",
        )

    @property
    def native_value(self):
        briefe = self.coordinator.data or []
        return briefe[-1]["absender"] if briefe else "Keine"

    @property
    def extra_state_attributes(self):
        briefe = self.coordinator.data or []
        letzter = briefe[-1] if briefe else {}
        return {
            "datum": _nur_datum(letzter.get("datum")),
            "bild": letzter.get("bild"),
            "anzahl": len(briefe),
            "briefe": [
                {
                    "absender": b.get("absender"),
                    "datum": _nur_datum(b.get("datum")),
                    "bild": b.get("bild"),
                }
                for b in reversed(briefe)
            ],
        }


def _nur_datum(wert):
    return wert.split(" ")[0] if wert else None

"""Sensor platform for Brottsplatskartan information."""
from __future__ import annotations

from collections import defaultdict
from datetime import timedelta

from brottsplatskartan import ATTRIBUTION, BrottsplatsKartan

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_APP_ID, CONF_AREA, DOMAIN, LOGGER

SCAN_INTERVAL = timedelta(minutes=30)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Brottsplatskartan sensor entry."""

    area = entry.data.get(CONF_AREA)
    latitude = entry.data.get(CONF_LATITUDE)
    longitude = entry.data.get(CONF_LONGITUDE)
    app = entry.data[CONF_APP_ID]
    name = entry.title

    bpk = BrottsplatsKartan(app=app, area=area, latitude=latitude, longitude=longitude)

    async_add_entities([BrottsplatskartanSensor(bpk, name, entry.entry_id)], True)


class BrottsplatskartanSensor(SensorEntity):
    """Representation of a Brottsplatskartan Sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(self, bpk: BrottsplatsKartan, name: str, entry_id: str) -> None:
        """Initialize the Brottsplatskartan sensor."""
        self._brottsplatskartan = bpk
        self._attr_unique_id = entry_id
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, entry_id)},
            manufacturer="Brottsplatskartan",
            name=name,
        )

    def update(self) -> None:
        """Update device state."""

        incident_counts: defaultdict[str, int] = defaultdict(int)
        incidents = self._brottsplatskartan.get_incidents()

        if incidents is False:
            LOGGER.debug("Problems fetching incidents")
            return

        for incident in incidents:
            if (incident_type := incident.get("title_type")) is not None:
                incident_counts[incident_type] += 1

        self._attr_extra_state_attributes = incident_counts
        self._attr_native_value = len(incidents)

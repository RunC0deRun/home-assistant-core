"""Support for Jellyfin remote commands."""

from collections.abc import Iterable
import time
from typing import Any, override

from homeassistant.components.remote import (
    ATTR_DELAY_SECS,
    ATTR_NUM_REPEATS,
    DEFAULT_DELAY_SECS,
    DEFAULT_NUM_REPEATS,
    RemoteEntity,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import LOGGER
from .coordinator import JellyfinConfigEntry, JellyfinDataUpdateCoordinator
from .entity import JellyfinClientEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: JellyfinConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Jellyfin remote from a config entry."""
    coordinator = entry.runtime_data

    @callback
    def handle_coordinator_update() -> None:
        """Add remote per client."""
        entities: list[RemoteEntity] = []
        for client_id, session_data in coordinator.data.items():
            if (
                client_id not in coordinator.remote_ids
                and session_data["SupportsRemoteControl"]
            ):
                entity = JellyfinRemote(coordinator, client_id)
                LOGGER.debug("Creating remote for client: %s", client_id)
                coordinator.remote_ids.add(client_id)
                entities.append(entity)
        async_add_entities(entities)

    handle_coordinator_update()

    entry.async_on_unload(coordinator.async_add_listener(handle_coordinator_update))


class JellyfinRemote(JellyfinClientEntity, RemoteEntity):
    """Defines a Jellyfin remote entity."""

    def __init__(
        self,
        coordinator: JellyfinDataUpdateCoordinator,
        client_id: str,
    ) -> None:
        """Initialize the Jellyfin Remote entity."""
        super().__init__(coordinator, client_id)
        self._attr_unique_id = f"{coordinator.server_id}-{client_id}"

    @property
    @override
    def is_on(self) -> bool:
        """Return if the client is on."""
        return self.session_data["IsActive"] if self.session_data else False

    @override
    def send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        """Send a command to the client."""
        num_repeats = kwargs.get(ATTR_NUM_REPEATS, DEFAULT_NUM_REPEATS)
        delay = kwargs.get(ATTR_DELAY_SECS, DEFAULT_DELAY_SECS)

        for _ in range(num_repeats):
            for single_command in command:
                self.coordinator.api_client.jellyfin.command(
                    self.session_id, single_command
                )
                time.sleep(delay)

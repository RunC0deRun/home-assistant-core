"""Tests for the Jellyfin remote platform."""

from unittest.mock import MagicMock

from pytest_homeassistant.common import MockConfigEntry

from homeassistant.components.remote import (
    ATTR_COMMAND,
    ATTR_DELAY_SECS,
    ATTR_HOLD_SECS,
    ATTR_NUM_REPEATS,
    DOMAIN as R_DOMAIN,
    SERVICE_SEND_COMMAND,
)
from homeassistant.const import ATTR_ENTITY_ID, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er


async def test_remote(
    hass: HomeAssistant,
    device_registry: dr.DeviceRegistry,
    entity_registry: er.EntityRegistry,
    init_integration: MockConfigEntry,
    mock_jellyfin: MagicMock,
    mock_api: MagicMock,
) -> None:
    """Test the Jellyfin remote."""
    state = hass.states.get("remote.jellyfin_device")
    state2 = hass.states.get("remote.jellyfin_device_two")
    state3 = hass.states.get("remote.jellyfin_device_three")
    state4 = hass.states.get("remote.jellyfin_device_four")

    assert state
    assert state2
    # Doesn't support remote control; remote not created
    assert state3 is None
    assert state4

    assert state.state == STATE_ON

    remote_entry = entity_registry.async_get(state4.entity_id)
    media_player_entry = entity_registry.async_get("media_player.jellyfin_device_four")
    assert remote_entry
    assert media_player_entry
    assert remote_entry.device_id == media_player_entry.device_id


async def test_services(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    mock_jellyfin: MagicMock,
    mock_api: MagicMock,
) -> None:
    """Test Jellyfin remote services."""
    state = hass.states.get("remote.jellyfin_device")
    assert state

    command = "Select"
    await hass.services.async_call(
        R_DOMAIN,
        SERVICE_SEND_COMMAND,
        {
            ATTR_ENTITY_ID: state.entity_id,
            ATTR_COMMAND: command,
            ATTR_NUM_REPEATS: 1,
            ATTR_DELAY_SECS: 0,
            ATTR_HOLD_SECS: 0,
        },
        blocking=True,
    )
    assert len(mock_api.command.mock_calls) == 1
    assert mock_api.command.mock_calls[0].args == (
        "SESSION-UUID",
        command,
    )

    command = "MoveLeft"
    await hass.services.async_call(
        R_DOMAIN,
        SERVICE_SEND_COMMAND,
        {
            ATTR_ENTITY_ID: state.entity_id,
            ATTR_COMMAND: command,
            ATTR_NUM_REPEATS: 2,
            ATTR_DELAY_SECS: 0,
            ATTR_HOLD_SECS: 0,
        },
        blocking=True,
    )
    assert len(mock_api.command.mock_calls) == 3
    assert mock_api.command.mock_calls[1].args == (
        "SESSION-UUID",
        command,
    )
    assert mock_api.command.mock_calls[2].args == (
        "SESSION-UUID",
        command,
    )

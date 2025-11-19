"""Tests for parser modules using real Controme HTML files."""
import pytest
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock
from bs4 import BeautifulSoup
from controme_scraper.parsers import (
    parse_room_temperature_html,
    parse_sensor_overview_html,
    parse_thermostat_html,
    parse_gateway_hardware
)
from controme_scraper.models import ThermostatMode, SensorType, Room

# Path to test fixtures (real HTML files from Controme system)
FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestRoomParserWithRealHTML:
    """Test room parsing with real Controme HTML."""

    def test_parse_real_room_overview(self):
        """Test parsing actual room_overview.html from Controme system."""
        html_file = FIXTURES_DIR / "room_overview.html"
        if not html_file.exists():
            pytest.skip("room_overview.html fixture not available")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html = f.read()
        
        # This HTML is from the room overview page, not individual room endpoint
        # Just verify it can be parsed without errors
        soup = BeautifulSoup(html, 'html.parser')
        assert soup is not None
        assert "Smart-Heat-OS" in html


class TestRoomParser:
    """Test room temperature HTML parsing."""

    def test_parse_room_basic(self):
        """Test parsing basic room data."""
        html = """
        <html>
            <span class="room_name">Wohnzimmer</span>
            <span class="temp">21.5</span>
            <span class="ziel" id="target_1">22.0</span>
        </html>
        """
        
        room = parse_room_temperature_html(1, html)
        
        assert room is not None
        assert room.name == "Wohnzimmer"
        assert room.current_temperature == 21.5
        assert room.target_temperature == 22.0
        assert room.room_id == 1

    def test_parse_room_with_valve_positions(self):
        """Test parsing room with valve positions."""
        html = """
        <html>
            <span class="room_name">Wohnzimmer</span>
            <span class="temp">21.5</span>
            <span class="ziel" id="target_1">22.0</span>
            <input class="beam-width-value" value="45" />
            <input class="beam-width-value" value="50" />
            <input class="beam-width-value" value="30" />
        </html>
        """
        
        room = parse_room_temperature_html(1, html)
        
        assert room is not None
        assert room.valve_positions == [45, 50, 30]

    def test_parse_room_with_offset(self):
        """Test parsing room with temperature offset."""
        html = """
        <html>
            <span class="room_name">Wohnzimmer</span>
            <span class="temp">21.5</span>
            <span class="ziel" id="target_1">22.0</span>
            <span class="heat5_room_offset">0.5</span>
        </html>
        """
        
        room = parse_room_temperature_html(1, html)
        
        assert room is not None
        assert room.target_temperature_offset == 0.5

    def test_parse_room_with_icon(self):
        """Test parsing room with icon."""
        html = """
        <html>
            <span class="room_name">Wohnzimmer</span>
            <span class="temp">21.5</span>
            <span class="ziel" id="target_1">22.0</span>
            <span class="room_icon"><img src="/icons/living.png" /></span>
        </html>
        """
        
        room = parse_room_temperature_html(1, html)
        
        assert room is not None
        assert room.icon == "/icons/living.png"

    def test_parse_room_empty_slot(self):
        """Test parsing empty/unused room slot."""
        html = """
        <html>
            <span class="room_name"></span>
        </html>
        """
        
        room = parse_room_temperature_html(1, html)
        
        # Should return None for empty slots
        assert room is None

    def test_parse_room_with_floor_name(self):
        """Test parsing room with floor name parameter."""
        html = """
        <html>
            <span class="room_name">Wohnzimmer</span>
            <span class="temp">21.5</span>
            <span class="ziel" id="target_1">22.0</span>
        </html>
        """
        
        room = parse_room_temperature_html(1, html, floor_name="Erdgeschoss")
        
        assert room is not None
        assert room.floor_name == "Erdgeschoss"


    def test_parse_room_malformed_temperature(self):
        """Test parsing with invalid temperature value."""
        html = """
        <html>
            <span class="room_name">Wohnzimmer</span>
            <span class="temp">invalid</span>
            <span class="ziel" id="target_1">22.0</span>
        </html>
        """
        
        room = parse_room_temperature_html(1, html)
        
        # Should still parse with current_temp as None
        assert room is not None
        assert room.current_temperature is None
        assert room.target_temperature == 22.0


class TestSensorOverviewParser:
    """Test sensor overview parsing with real Controme HTML."""

    def test_parse_real_sensor_config(self):
        """Test parsing actual sensor_config.html from Controme system."""
        html_file = FIXTURES_DIR / "sensor_config.html"
        if not html_file.exists():
            pytest.skip("sensor_config.html fixture not available")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html = f.read()
        
        sensors = parse_sensor_overview_html(html)
        
        # Should parse at least some sensors from real file
        assert isinstance(sensors, list)
        if len(sensors) > 0:
            # Verify sensor structure
            sensor = sensors[0]
            assert hasattr(sensor, 'sensor_id')
            assert hasattr(sensor, 'name')
            assert hasattr(sensor, 'sensor_type')
            assert hasattr(sensor, 'value')

    def test_parse_sensors_return_flow_type(self):
        """Test parsing return flow sensor type detection."""
        html = """
        <html>
            <div class="ui-collapsible">
                <ul class="room_list" data-id="1">
                    <span class="room_name">Wohnzimmer</span>
                    <li><a>RL Temp <small class="no-link">45.0</small></a></li>
                </ul>
            </div>
        </html>
        """
        
        sensors = parse_sensor_overview_html(html)
        
        assert len(sensors) == 1
        assert sensors[0].sensor_type == SensorType.RETURN_FLOW

    def test_parse_sensors_empty(self):
        """Test parsing with no sensors."""
        html = "<html><body></body></html>"
        
        sensors = parse_sensor_overview_html(html)
        
        assert sensors == []


class TestActuatorConfigParser:
    """Test actuator config parsing with real Controme data."""

    def test_parse_real_actuator_config(self):
        """Test parsing actual actuator_config.html from Controme system."""
        html_file = FIXTURES_DIR / "actuator_config.html"
        if not html_file.exists():
            pytest.skip("actuator_config.html fixture not available")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html = f.read()
        
        hardware = parse_gateway_hardware(html)
        
        # Should parse hardware info without errors
        assert isinstance(hardware, dict)

    def test_parse_gateway_hardware_empty(self):
        """Test parsing empty gateway hardware."""
        html = "<html><body></body></html>"
        
        hardware = parse_gateway_hardware(html)
        
        # Should return empty dict
        assert hardware == {}


class TestParserEdgeCases:
    """Test parser edge cases and error handling."""

    def test_parse_room_with_unicode_characters(self):
        """Test parsing with German umlauts and special chars."""
        html = """
        <html>
            <span class="room_name">Küche mit Eßplatz</span>
            <span class="temp">21.5</span>
            <span class="ziel" id="target_1">22.0</span>
        </html>
        """
        
        room = parse_room_temperature_html(1, html)
        
        assert room is not None
        assert room.name == "Küche mit Eßplatz"

    def test_parse_room_with_whitespace(self):
        """Test parsing with extra whitespace."""
        html = """
        <html>
            <span class="room_name">  Wohnzimmer  </span>
            <span class="temp">  21.5  </span>
            <span class="ziel" id="target_1">  22.0  </span>
        </html>
        """
        
        room = parse_room_temperature_html(1, html)
        
        # Parser should strip whitespace
        assert room is not None
        assert room.name == "Wohnzimmer"

    def test_parse_sensor_invalid_value(self):
        """Test parsing sensor with invalid numeric value."""
        html = """
        <html>
            <div class="ui-collapsible">
                <ul class="room_list" data-id="1">
                    <span class="room_name">Wohnzimmer</span>
                    <li><a>Temp <small class="no-link">invalid</small></a></li>
                </ul>
            </div>
        </html>
        """
        
        sensors = parse_sensor_overview_html(html)
        
        # Should skip invalid sensors
        assert sensors == []

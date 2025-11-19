"""Tests for data models."""
import pytest
from controme_scraper.models import Room, Thermostat, Sensor, Gateway, SensorType, ThermostatMode


class TestRoom:
    """Test Room model."""

    def test_room_creation(self):
        """Test creating a Room instance."""
        room = Room(
            id=1,
            name="Wohnzimmer",
            floor_name="Erdgeschoss",
            current_temperature=21.5,
            target_temperature=22.0,
            valve_positions=[50, 60, 40],
        )
        
        assert room.id == 1
        assert room.name == "Wohnzimmer"
        assert room.floor_name == "Erdgeschoss"
        assert room.current_temperature == 21.5
        assert room.target_temperature == 22.0
        assert room.valve_positions == [50, 60, 40]

    def test_room_is_heating_with_open_valves(self):
        """Test is_heating returns True when valves are open."""
        room = Room(
            id=1,
            name="Wohnzimmer",
            current_temperature=21.0,
            target_temperature=22.0,
            valve_positions=[50, 30, 20],
        )
        
        assert room.is_heating is True

    def test_room_is_heating_with_closed_valves(self):
        """Test is_heating returns False when all valves closed."""
        room = Room(
            id=1,
            name="Wohnzimmer",
            current_temperature=22.0,
            target_temperature=22.0,
            valve_positions=[0, 0, 0],
        )
        
        assert room.is_heating is False

    def test_room_is_heating_with_no_valves(self):
        """Test is_heating returns False when no valve data."""
        room = Room(
            id=1,
            name="Wohnzimmer",
            current_temperature=21.0,
            target_temperature=22.0,
            valve_positions=[],
        )
        
        assert room.is_heating is False

    def test_room_average_valve_position(self):
        """Test average valve position calculation."""
        room = Room(
            id=1,
            name="Wohnzimmer",
            current_temperature=21.0,
            target_temperature=22.0,
            valve_positions=[50, 60, 40],
        )
        
        assert room.average_valve_position == 50.0

    def test_room_average_valve_position_no_valves(self):
        """Test average valve position with no valves."""
        room = Room(
            id=1,
            name="Wohnzimmer",
            current_temperature=21.0,
            target_temperature=22.0,
            valve_positions=[],
        )
        
        assert room.average_valve_position is None

    def test_room_relative_valve_positions(self):
        """Test relative valve position calculation."""
        room = Room(
            id=1,
            name="Wohnzimmer",
            current_temperature=21.0,
            target_temperature=22.0,
            valve_positions=[50, 60, 40],
            max_valve_positions=[100, 80, 100],
        )
        
        # 50/100=50%, 60/80=75%, 40/100=40%
        expected = [50.0, 75.0, 40.0]
        assert room.relative_valve_positions == expected

    def test_room_average_relative_valve_position(self):
        """Test average relative valve position."""
        room = Room(
            id=1,
            name="Wohnzimmer",
            current_temperature=21.0,
            target_temperature=22.0,
            valve_positions=[50, 60, 40],
            max_valve_positions=[100, 80, 100],
        )
        
        # (50% + 75% + 40%) / 3 = 55%
        assert room.average_relative_valve_position == 55.0


class TestThermostat:
    """Test Thermostat model."""

    def test_thermostat_creation(self):
        """Test creating a Thermostat instance."""
        thermostat = Thermostat(
            device_id="1*1*1*1",
            name="Wohnzimmer Thermostat",
            mac_address="00:11:22:33:44:55",
            current_temperature=21.5,
            target_temperature=22.0,
            assigned_room=1,
            firmware_version="1.2.3",
        )
        
        assert thermostat.device_id == "1*1*1*1"
        assert thermostat.name == "Wohnzimmer Thermostat"
        assert thermostat.mac_address == "00:11:22:33:44:55"
        assert thermostat.current_temperature == 21.5
        assert thermostat.target_temperature == 22.0
        assert thermostat.assigned_room == 1

    def test_thermostat_is_heating(self):
        """Test thermostat heating status based on valve positions."""
        thermostat = Thermostat(
            device_id="1*1*1*1",
            name="Wohnzimmer",
            current_temperature=21.0,
            target_temperature=22.0,
            valve_positions=[50, 30],
        )
        
        assert thermostat.is_heating is True

    def test_thermostat_not_heating(self):
        """Test thermostat not heating when valves closed."""
        thermostat = Thermostat(
            device_id="1*1*1*1",
            name="Wohnzimmer",
            current_temperature=22.0,
            target_temperature=22.0,
            valve_positions=[0, 0],
        )
        
        assert thermostat.is_heating is False


class TestSensor:
    """Test Sensor model."""

    def test_sensor_creation_temperature(self):
        """Test creating a temperature Sensor."""
        sensor = Sensor(
            id=1,
            name="Außentemperatur",
            type=SensorType.TEMPERATURE,
            value=5.2,
            unit="°C",
        )
        
        assert sensor.id == 1
        assert sensor.name == "Außentemperatur"
        assert sensor.type == SensorType.TEMPERATURE
        assert sensor.value == 5.2
        assert sensor.unit == "°C"

    def test_sensor_creation_humidity(self):
        """Test creating a humidity Sensor."""
        sensor = Sensor(
            id=2,
            name="Luftfeuchtigkeit",
            type=SensorType.HUMIDITY,
            value=65.0,
            unit="%",
        )
        
        assert sensor.type == SensorType.HUMIDITY
        assert sensor.value == 65.0


class TestGateway:
    """Test Gateway model."""

    def test_gateway_creation(self):
        """Test creating a Gateway instance."""
        gateway = Gateway(
            heating_demand=45.5,
            boiler_active=True,
            rooms_heating=3,
            total_rooms=7,
        )
        
        assert gateway.heating_demand == 45.5
        assert gateway.boiler_active is True
        assert gateway.rooms_heating == 3
        assert gateway.total_rooms == 7

    def test_gateway_heating_demand_percentage(self):
        """Test heating demand represents percentage."""
        gateway = Gateway(
            heating_demand=75.5,
            boiler_active=True,
        )
        
        assert 0 <= gateway.heating_demand <= 100


class TestThermostatMode:
    """Test ThermostatMode enum."""

    def test_thermostat_mode_values(self):
        """Test ThermostatMode enum values."""
        assert ThermostatMode.AUTO.value == "auto"
        assert ThermostatMode.MANUAL.value == "manual"
        assert ThermostatMode.OFF.value == "off"


class TestSensorType:
    """Test SensorType enum."""

    def test_sensor_type_values(self):
        """Test SensorType enum values."""
        assert SensorType.TEMPERATURE.value == "temperature"
        assert SensorType.HUMIDITY.value == "humidity"
        assert SensorType.PRESSURE.value == "pressure"

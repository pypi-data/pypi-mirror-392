"""Tests for ContromeController."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from controme_scraper import ContromeController
from controme_scraper.models import Room, Thermostat, Sensor, Gateway


class TestContromeController:
    """Test ContromeController functionality."""

    @patch('controme_scraper.controller.SessionManager')
    @patch('controme_scraper.controller.WebClient')
    def test_controller_init(self, mock_web_client, mock_session_manager):
        """Test ContromeController initialization."""
        mock_session = Mock()
        mock_session_manager.return_value.logon.return_value = mock_session
        
        controller = ContromeController(
            host="http://192.168.1.10",
            username="testuser",
            password="testpass",
            house_id=1
        )
        
        assert controller.host == "http://192.168.1.10/"  # Trailing slash added
        assert controller.house_id == 1
        mock_session_manager.assert_called_once_with(
            url="http://192.168.1.10/",
            user="testuser",
            password="testpass"
        )

    @patch('controme_scraper.controller.SessionManager')
    @patch('controme_scraper.controller.WebClient')
    def test_controller_adds_trailing_slash(self, mock_web_client, mock_session_manager):
        """Test that controller adds trailing slash to URL."""
        mock_session = Mock()
        mock_session_manager.return_value.logon.return_value = mock_session
        
        controller = ContromeController(
            host="http://192.168.1.10",
            username="testuser",
            password="testpass"
        )
        
        assert controller.host.endswith("/")

    @patch('controme_scraper.controller.SessionManager')
    @patch('controme_scraper.controller.WebClient')
    def test_get_rooms(self, mock_web_client, mock_session_manager):
        """Test getting rooms."""
        mock_session = Mock()
        mock_session_manager.return_value.logon.return_value = mock_session
        
        # Mock WebClient instance
        mock_client_instance = Mock()
        mock_web_client.return_value = mock_client_instance
        mock_client_instance.get_rooms.return_value = [
            {"id": 1, "name": "Wohnzimmer", "temperature": 21.5}
        ]
        
        controller = ContromeController(
            host="http://192.168.1.10",
            username="testuser",
            password="testpass"
        )
        
        rooms = controller.get_rooms()
        
        assert isinstance(rooms, list)
        mock_client_instance.get_rooms.assert_called_once()

    @patch('controme_scraper.controller.SessionManager')
    @patch('controme_scraper.controller.WebClient')
    def test_get_thermostats(self, mock_web_client, mock_session_manager):
        """Test getting thermostats."""
        mock_session = Mock()
        mock_session_manager.return_value.logon.return_value = mock_session
        
        mock_client_instance = Mock()
        mock_web_client.return_value = mock_client_instance
        mock_client_instance.get_thermostats.return_value = [
            {"device_id": "1*1*1*1", "name": "Wohnzimmer"}
        ]
        
        controller = ContromeController(
            host="http://192.168.1.10",
            username="testuser",
            password="testpass"
        )
        
        thermostats = controller.get_thermostats()
        
        assert isinstance(thermostats, list)
        mock_client_instance.get_thermostats.assert_called_once()

    @patch('controme_scraper.controller.SessionManager')
    @patch('controme_scraper.controller.WebClient')
    def test_get_sensors(self, mock_web_client, mock_session_manager):
        """Test getting sensors."""
        mock_session = Mock()
        mock_session_manager.return_value.logon.return_value = mock_session
        
        mock_client_instance = Mock()
        mock_web_client.return_value = mock_client_instance
        mock_client_instance.get_sensors.return_value = [
            {"id": 1, "name": "Außentemperatur", "value": 5.2}
        ]
        
        controller = ContromeController(
            host="http://192.168.1.10",
            username="testuser",
            password="testpass"
        )
        
        sensors = controller.get_sensors()
        
        assert isinstance(sensors, list)
        mock_client_instance.get_sensors.assert_called_once()

    @patch('controme_scraper.controller.SessionManager')
    @patch('controme_scraper.controller.WebClient')
    def test_multi_house_support(self, mock_web_client, mock_session_manager):
        """Test multi-house support with different house_id."""
        mock_session = Mock()
        mock_session_manager.return_value.logon.return_value = mock_session
        
        # House 1
        controller1 = ContromeController(
            host="http://192.168.1.10",
            username="testuser",
            password="testpass",
            house_id=1
        )
        assert controller1.house_id == 1
        
        # House 2
        controller2 = ContromeController(
            host="http://192.168.1.10",
            username="testuser",
            password="testpass",
            house_id=2
        )
        assert controller2.house_id == 2

    @patch('controme_scraper.controller.SessionManager')
    @patch('controme_scraper.controller.WebClient')
    def test_default_house_id(self, mock_web_client, mock_session_manager):
        """Test default house_id is 1."""
        mock_session = Mock()
        mock_session_manager.return_value.logon.return_value = mock_session
        
        controller = ContromeController(
            host="http://192.168.1.10",
            username="testuser",
            password="testpass"
        )
        
        assert controller.house_id == 1

    @patch('controme_scraper.controller.SessionManager')
    @patch('controme_scraper.controller.WebClient')
    def test_web_client_access(self, mock_web_client, mock_session_manager):
        """Test access to web_client property."""
        mock_session = Mock()
        mock_session_manager.return_value.logon.return_value = mock_session
        
        mock_client_instance = Mock()
        mock_web_client.return_value = mock_client_instance
        
        controller = ContromeController(
            host="http://192.168.1.10",
            username="testuser",
            password="testpass"
        )
        
        assert controller.web_client == mock_client_instance

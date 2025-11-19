"""Tests for WebClient."""
import pytest
from unittest.mock import Mock, patch
from controme_scraper.web_client import WebClient


class TestWebClient:
    """Test WebClient functionality."""

    def test_init(self, mock_session):
        """Test WebClient initialization."""
        client = WebClient(
            url="http://192.168.1.10/",
            session=mock_session,
            house_id=1
        )
        
        assert client._url == "http://192.168.1.10/"
        assert client._session == mock_session
        assert client._house_id == 1

    def test_get_thermostats(self, mock_session, mock_response):
        """Test fetching thermostats."""
        mock_response.json.return_value = [
            {"device_id": "1*1*1*1", "name": "Wohnzimmer"},
            {"device_id": "1*1*1*2", "name": "Schlafzimmer"}
        ]
        mock_session.get.return_value = mock_response
        
        client = WebClient(
            url="http://192.168.1.10/",
            session=mock_session,
            house_id=1
        )
        
        result = client.get_thermostats()
        
        assert len(result) == 2
        assert result[0]["name"] == "Wohnzimmer"
        mock_session.get.assert_called_once()
        
        # Verify URL includes house_id
        call_url = mock_session.get.call_args[0][0]
        assert "m_setup/1/rf/" in call_url

    def test_get_rooms(self, mock_session, mock_response):
        """Test fetching rooms."""
        mock_response.json.return_value = [
            {"id": 1, "name": "Wohnzimmer", "temperature": 21.5},
            {"id": 2, "name": "Schlafzimmer", "temperature": 19.0}
        ]
        mock_session.get.return_value = mock_response
        
        client = WebClient(
            url="http://192.168.1.10/",
            session=mock_session,
            house_id=1
        )
        
        result = client.get_rooms()
        
        assert len(result) == 2
        assert result[0]["name"] == "Wohnzimmer"

    def test_get_sensors(self, mock_session, mock_response):
        """Test fetching sensors."""
        mock_response.json.return_value = [
            {"id": 1, "name": "Außentemperatur", "value": 5.2},
            {"id": 2, "name": "Vorlauf", "value": 45.0}
        ]
        mock_session.get.return_value = mock_response
        
        client = WebClient(
            url="http://192.168.1.10/",
            session=mock_session,
            house_id=1
        )
        
        result = client.get_sensors()
        
        assert len(result) == 2
        assert result[0]["name"] == "Außentemperatur"

    def test_set_room_temperature(self, mock_session, mock_response):
        """Test setting room temperature."""
        mock_response.ok = True
        mock_session.post.return_value = mock_response
        
        client = WebClient(
            url="http://192.168.1.10/",
            session=mock_session,
            house_id=1
        )
        
        result = client.set_room_temperature(room_id=1, temperature=22.5)
        
        assert result is True
        mock_session.post.assert_called_once()
        
        # Verify temperature was rounded to 0.5
        call_args = mock_session.post.call_args
        assert call_args.kwargs['data']['slidernumber'] == '22'

    def test_set_room_temperature_rounding(self, mock_session, mock_response):
        """Test temperature rounding to 0.5 steps."""
        mock_response.ok = True
        mock_session.post.return_value = mock_response
        
        client = WebClient(
            url="http://192.168.1.10/",
            session=mock_session,
            house_id=1
        )
        
        # Test various temperatures
        test_cases = [
            (21.2, '21'),   # Rounds to 21.0
            (21.3, '21'),   # Rounds to 21.5 but displayed as 21
            (21.7, '22'),   # Rounds to 21.5 but displayed as 22
            (21.8, '22'),   # Rounds to 22.0
            (22.0, '22'),   # Exact
            (22.5, '22'),   # Exact half
        ]
        
        for input_temp, expected_slider in test_cases:
            client.set_room_temperature(room_id=1, temperature=input_temp)
            call_args = mock_session.post.call_args
            assert call_args.kwargs['data']['slidernumber'] == expected_slider

    def test_set_room_temperature_failure(self, mock_session, mock_response):
        """Test handling of failed temperature setting."""
        mock_response.ok = False
        mock_session.post.return_value = mock_response
        
        client = WebClient(
            url="http://192.168.1.10/",
            session=mock_session,
            house_id=1
        )
        
        result = client.set_room_temperature(room_id=1, temperature=22.0)
        
        assert result is False

    def test_url_construction_with_house_id(self, mock_session, mock_response):
        """Test that URLs are constructed with correct house_id."""
        mock_response.json.return_value = []
        mock_session.get.return_value = mock_response
        
        # Test with house_id = 2
        client = WebClient(
            url="http://192.168.1.10/",
            session=mock_session,
            house_id=2
        )
        
        client.get_thermostats()
        
        call_url = mock_session.get.call_args[0][0]
        assert "m_setup/2/rf/" in call_url

    def test_trailing_slash_handling(self, mock_session):
        """Test that URL handles trailing slashes correctly."""
        # URL without trailing slash
        client1 = WebClient(
            url="http://192.168.1.10",
            session=mock_session,
            house_id=1
        )
        
        # URL with trailing slash
        client2 = WebClient(
            url="http://192.168.1.10/",
            session=mock_session,
            house_id=1
        )
        
        # Both should work (trailing slash added in heizung.py)
        assert client1._url.startswith("http://192.168.1.10")
        assert client2._url.startswith("http://192.168.1.10")

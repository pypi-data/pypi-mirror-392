"""Tests for SessionManager."""
import pytest
from unittest.mock import Mock, patch, mock_open
from controme_scraper.session_manager import SessionManager


class TestSessionManager:
    """Test SessionManager functionality."""

    def test_init(self):
        """Test SessionManager initialization."""
        manager = SessionManager(
            url="http://192.168.1.10/",
            user="testuser",
            password="testpass"
        )
        
        assert manager.base_url == "http://192.168.1.10/"
        assert manager._user == "testuser"
        assert manager._password == "testpass"
        assert manager._session is None

    def test_generate_filename(self):
        """Test session filename generation."""
        manager = SessionManager(
            url="http://192.168.1.10/",
            user="testuser",
            password="testpass"
        )
        
        filename = manager._generate_filename("testuser", "testpass")
        
        # Should be a SHA256 hash + .session
        assert filename.endswith(".session")
        assert len(filename) == 64 + 8  # 64 hex chars + ".session"

    def test_generate_filename_consistency(self):
        """Test that same credentials generate same filename."""
        manager = SessionManager(
            url="http://192.168.1.10/",
            user="testuser",
            password="testpass"
        )
        
        filename1 = manager._generate_filename("testuser", "testpass")
        filename2 = manager._generate_filename("testuser", "testpass")
        
        assert filename1 == filename2

    @patch('controme_scraper.session_manager.requests.Session')
    def test_load_session_creates_new(self, mock_session_class):
        """Test that _load_session creates new session if file not found."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        manager = SessionManager(
            url="http://192.168.1.10/",
            user="testuser",
            password="testpass"
        )
        
        with patch('builtins.open', side_effect=FileNotFoundError):
            with patch.object(manager, '_validate_session', return_value=False):
                result = manager._load_session()
        
        assert result is False
        assert manager._session == mock_session

    @patch('controme_scraper.session_manager.requests.Session')
    def test_validate_session_success(self, mock_session_class, mock_response):
        """Test successful session validation."""
        mock_session = Mock()
        mock_response.text = '<html><title>Smart-Heat-OS - Temperaturüberwachung</title></html>'
        mock_session.get.return_value = mock_response
        
        manager = SessionManager(
            url="http://192.168.1.10/",
            user="testuser",
            password="testpass"
        )
        manager._session = mock_session
        
        result = manager._validate_session()
        
        assert result is True
        mock_session.get.assert_called_once()

    @patch('controme_scraper.session_manager.requests.Session')
    def test_validate_session_failure(self, mock_session_class, mock_response):
        """Test failed session validation."""
        mock_session = Mock()
        mock_response.text = '<html><title>Login Page</title></html>'
        mock_session.get.return_value = mock_response
        
        manager = SessionManager(
            url="http://192.168.1.10/",
            user="testuser",
            password="testpass"
        )
        manager._session = mock_session
        
        result = manager._validate_session()
        
        assert result is False

    @patch('controme_scraper.session_manager.requests.Session')
    def test_logon_with_valid_session(self, mock_session_class):
        """Test logon when session is already valid."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        manager = SessionManager(
            url="http://192.168.1.10/",
            user="testuser",
            password="testpass"
        )
        
        with patch.object(manager, '_load_session', return_value=True):
            result = manager.logon(login_url="accounts/m_login/")
        
        assert result == mock_session
        # Should not attempt to login if session is valid
        mock_session.post.assert_not_called()

    @patch('controme_scraper.session_manager.requests.Session')
    def test_logon_performs_login(self, mock_session_class, mock_response):
        """Test logon performs actual login when session invalid."""
        mock_session = Mock()
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        manager = SessionManager(
            url="http://192.168.1.10/",
            user="testuser",
            password="testpass"
        )
        
        with patch.object(manager, '_load_session', return_value=False):
            with patch.object(manager, '_validate_session', return_value=True):
                with patch.object(manager, '_save_session'):
                    result = manager.logon(login_url="accounts/m_login/")
        
        assert result == mock_session
        mock_session.post.assert_called_once()
        
        # Verify login data was sent
        call_args = mock_session.post.call_args
        assert 'data' in call_args.kwargs
        assert call_args.kwargs['data']['username'] == 'testuser'
        assert call_args.kwargs['data']['password'] == 'testpass'

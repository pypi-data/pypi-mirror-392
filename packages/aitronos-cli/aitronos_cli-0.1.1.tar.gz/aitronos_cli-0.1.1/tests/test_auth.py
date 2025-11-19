"""Tests for authentication manager."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta
import jwt as pyjwt

from aitronos_cli.auth import AuthManager


class TestAuthManager:
    """Test authentication manager."""
    
    @pytest.fixture
    def auth_manager(self):
        """Create auth manager instance."""
        with patch('aitronos_cli.auth.config') as mock_config:
            mock_config.load_auth.return_value = None
            return AuthManager()
    
    def test_token_type_validation_on_login(self, auth_manager):
        """Test that login validates token types and prevents swapping."""
        # Create mock tokens with correct types
        access_payload = {
            'sub': 'usr_123',
            'type': 'access',
            'exp': (datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()
        }
        refresh_payload = {
            'sub': 'usr_123',
            'type': 'refresh',
            'exp': (datetime.now(timezone.utc) + timedelta(days=30)).timestamp()
        }
        
        access_token = pyjwt.encode(access_payload, 'secret', algorithm='HS256')
        refresh_token = pyjwt.encode(refresh_payload, 'secret', algorithm='HS256')
        
        with patch('aitronos_cli.auth.AitronosAPIClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            # Mock login response
            mock_client.login.return_value = {'email_key': 'key123'}
            
            # Mock verify response with correct tokens
            mock_client.verify_login.return_value = {
                'token': access_token,
                'refreshToken': refresh_token,
                'user': {'id': 'usr_123', 'email': 'test@example.com'}
            }
            
            with patch.object(auth_manager.config, 'save_auth') as mock_save:
                with patch.object(auth_manager.config, 'get_api_url', return_value='http://test.com'):
                    result = auth_manager.login('test@example.com', 'password')
                    
                    assert result is True
                    
                    # Verify tokens were saved correctly
                    saved_data = mock_save.call_args[0][0]
                    assert saved_data['access_token'] == access_token
                    assert saved_data['refresh_token'] == refresh_token
    
    def test_token_type_swap_detection(self, auth_manager):
        """Test that swapped tokens are detected and corrected."""
        # Create tokens with SWAPPED types (access has refresh type, vice versa)
        wrong_access_payload = {
            'sub': 'usr_123',
            'type': 'refresh',  # WRONG!
            'exp': (datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()
        }
        wrong_refresh_payload = {
            'sub': 'usr_123',
            'type': 'access',  # WRONG!
            'exp': (datetime.now(timezone.utc) + timedelta(days=30)).timestamp()
        }
        
        wrong_access_token = pyjwt.encode(wrong_access_payload, 'secret', algorithm='HS256')
        wrong_refresh_token = pyjwt.encode(wrong_refresh_payload, 'secret', algorithm='HS256')
        
        with patch('aitronos_cli.auth.AitronosAPIClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            mock_client.login.return_value = {'email_key': 'key123'}
            
            # Return swapped tokens
            mock_client.verify_login.return_value = {
                'token': wrong_access_token,  # Has 'refresh' type
                'refreshToken': wrong_refresh_token,  # Has 'access' type
                'user': {'id': 'usr_123', 'email': 'test@example.com'}
            }
            
            with patch.object(auth_manager.config, 'save_auth') as mock_save:
                with patch.object(auth_manager.config, 'get_api_url', return_value='http://test.com'):
                    result = auth_manager.login('test@example.com', 'password')
                    
                    assert result is True
                    
                    # Verify tokens were swapped back correctly
                    saved_data = mock_save.call_args[0][0]
                    
                    # The token with 'access' type should be saved as access_token
                    decoded_access = pyjwt.decode(saved_data['access_token'], options={"verify_signature": False})
                    assert decoded_access['type'] == 'access'
                    
                    # The token with 'refresh' type should be saved as refresh_token
                    decoded_refresh = pyjwt.decode(saved_data['refresh_token'], options={"verify_signature": False})
                    assert decoded_refresh['type'] == 'refresh'
    
    def test_automatic_token_refresh_on_expiry(self, auth_manager):
        """Test that expired tokens are automatically refreshed."""
        # Create expired access token
        expired_payload = {
            'sub': 'usr_123',
            'type': 'access',
            'exp': (datetime.now(timezone.utc) - timedelta(minutes=1)).timestamp()  # Expired!
        }
        expired_token = pyjwt.encode(expired_payload, 'secret', algorithm='HS256')
        
        # Create valid refresh token
        refresh_payload = {
            'sub': 'usr_123',
            'type': 'refresh',
            'exp': (datetime.now(timezone.utc) + timedelta(days=30)).timestamp()
        }
        refresh_token = pyjwt.encode(refresh_payload, 'secret', algorithm='HS256')
        
        # Create new access token (from refresh)
        new_access_payload = {
            'sub': 'usr_123',
            'type': 'access',
            'exp': (datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()
        }
        new_access_token = pyjwt.encode(new_access_payload, 'secret', algorithm='HS256')
        
        with patch.object(auth_manager.config, 'load_auth') as mock_load:
            # First call returns expired token
            mock_load.return_value = {
                'access_token': expired_token,
                'refresh_token': refresh_token
            }
            
            with patch('aitronos_cli.auth.AitronosAPIClient') as mock_client_class:
                mock_client = Mock()
                mock_client_class.return_value = mock_client
                
                # Mock refresh response
                mock_client.refresh_token.return_value = {
                    'token': new_access_token
                }
                
                with patch.object(auth_manager.config, 'save_auth') as mock_save:
                    with patch.object(auth_manager.config, 'get_api_url', return_value='http://test.com'):
                        # Second call after refresh returns new token
                        mock_load.side_effect = [
                            {'access_token': expired_token, 'refresh_token': refresh_token},
                            {'access_token': new_access_token, 'refresh_token': refresh_token}
                        ]
                        
                        # This should trigger automatic refresh
                        token = auth_manager.get_access_token(auto_refresh=True)
                        
                        # Verify refresh was called
                        mock_client.refresh_token.assert_called_once_with(refresh_token)
                        
                        # Verify new token was saved
                        assert mock_save.called
                        
                        # Verify new token is returned
                        assert token == new_access_token
    
    def test_refresh_token_field_name_compatibility(self, auth_manager):
        """Test that refresh endpoint response field names are handled correctly."""
        refresh_payload = {
            'sub': 'usr_123',
            'type': 'refresh',
            'exp': (datetime.now(timezone.utc) + timedelta(days=30)).timestamp()
        }
        refresh_token = pyjwt.encode(refresh_payload, 'secret', algorithm='HS256')
        
        new_access_payload = {
            'sub': 'usr_123',
            'type': 'access',
            'exp': (datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()
        }
        new_access_token = pyjwt.encode(new_access_payload, 'secret', algorithm='HS256')
        
        with patch('aitronos_cli.auth.AitronosAPIClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            # Backend returns 'token' not 'access_token'
            mock_client.refresh_token.return_value = {
                'token': new_access_token  # Field name is 'token'
            }
            
            with patch.object(auth_manager.config, 'load_auth') as mock_load:
                mock_load.return_value = {
                    'access_token': 'old_token',
                    'refresh_token': refresh_token
                }
                
                with patch.object(auth_manager.config, 'save_auth') as mock_save:
                    with patch.object(auth_manager.config, 'get_api_url', return_value='http://test.com'):
                        result = auth_manager.refresh_access_token()
                        
                        assert result is True
                        
                        # Verify the new token was extracted from 'token' field
                        saved_data = mock_save.call_args[0][0]
                        assert saved_data['access_token'] == new_access_token
    
    def test_token_expiry_within_5_minutes_triggers_refresh(self, auth_manager):
        """Test that tokens expiring within 5 minutes are refreshed proactively."""
        # Create token expiring in 3 minutes
        soon_expired_payload = {
            'sub': 'usr_123',
            'type': 'access',
            'exp': (datetime.now(timezone.utc) + timedelta(minutes=3)).timestamp()
        }
        soon_expired_token = pyjwt.encode(soon_expired_payload, 'secret', algorithm='HS256')
        
        refresh_payload = {
            'sub': 'usr_123',
            'type': 'refresh',
            'exp': (datetime.now(timezone.utc) + timedelta(days=30)).timestamp()
        }
        refresh_token = pyjwt.encode(refresh_payload, 'secret', algorithm='HS256')
        
        new_access_payload = {
            'sub': 'usr_123',
            'type': 'access',
            'exp': (datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()
        }
        new_access_token = pyjwt.encode(new_access_payload, 'secret', algorithm='HS256')
        
        with patch.object(auth_manager.config, 'load_auth') as mock_load:
            mock_load.return_value = {
                'access_token': soon_expired_token,
                'refresh_token': refresh_token
            }
            
            with patch('aitronos_cli.auth.AitronosAPIClient') as mock_client_class:
                mock_client = Mock()
                mock_client_class.return_value = mock_client
                
                mock_client.refresh_token.return_value = {
                    'token': new_access_token
                }
                
                with patch.object(auth_manager.config, 'save_auth'):
                    with patch.object(auth_manager.config, 'get_api_url', return_value='http://test.com'):
                        mock_load.side_effect = [
                            {'access_token': soon_expired_token, 'refresh_token': refresh_token},
                            {'access_token': new_access_token, 'refresh_token': refresh_token}
                        ]
                        
                        # Should trigger refresh even though not expired yet
                        token = auth_manager.get_access_token(auto_refresh=True)
                        
                        # Verify refresh was called
                        mock_client.refresh_token.assert_called_once()
    
    def test_is_authenticated_with_valid_token(self, auth_manager):
        """Test authentication check with valid token."""
        valid_payload = {
            'sub': 'usr_123',
            'type': 'access',
            'exp': (datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()
        }
        valid_token = pyjwt.encode(valid_payload, 'secret', algorithm='HS256')
        
        with patch.object(auth_manager.config, 'load_auth') as mock_load:
            mock_load.return_value = {
                'access_token': valid_token
            }
            
            assert auth_manager.is_authenticated() is True
    
    def test_is_authenticated_with_expired_token(self, auth_manager):
        """Test authentication check with expired token."""
        expired_payload = {
            'sub': 'usr_123',
            'type': 'access',
            'exp': (datetime.now(timezone.utc) - timedelta(hours=1)).timestamp()
        }
        expired_token = pyjwt.encode(expired_payload, 'secret', algorithm='HS256')
        
        with patch.object(auth_manager.config, 'load_auth') as mock_load:
            mock_load.return_value = {
                'access_token': expired_token
            }
            
            assert auth_manager.is_authenticated() is False
    
    def test_is_authenticated_with_no_token(self, auth_manager):
        """Test authentication check with no token."""
        with patch.object(auth_manager.config, 'load_auth') as mock_load:
            mock_load.return_value = None
            
            assert auth_manager.is_authenticated() is False


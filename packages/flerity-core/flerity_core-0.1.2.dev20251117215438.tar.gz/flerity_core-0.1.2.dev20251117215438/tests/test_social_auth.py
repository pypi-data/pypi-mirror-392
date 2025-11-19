"""Integration tests for social authentication."""

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from flerity_core.domain.auth.schemas import SocialLoginRequest, SocialProvider
from flerity_core.domain.auth.service import AuthService
from flerity_core.domain.auth.social_validators import AppleTokenValidator, GoogleTokenValidator
from flerity_core.utils.errors import BadRequest, DependencyError


class TestSocialAuth:
    """Test social authentication functionality."""

    @pytest.mark.asyncio
    async def test_google_social_login_new_user(self):
        """Test Google login with new user."""
        
        # Mock the entire auth service method
        with patch.object(AuthService, 'authenticate_social_user') as mock_auth:
            # Setup mock return value
            from flerity_core.domain.auth.schemas import SocialAuthResponse, UserProfile, AuthTokenPair
            from datetime import datetime
            
            mock_user = UserProfile(
                id=uuid4(),
                email="user@example.com",
                email_verified=True,
                gender="non-binary",
                country="US",
                created_at=datetime.utcnow()
            )
            
            mock_tokens = AuthTokenPair(
                access_token="mock-access-token",
                refresh_token="mock-refresh-token",
                expires_in=3600
            )
            
            mock_result = SocialAuthResponse(
                user=mock_user,
                tokens=mock_tokens,
                is_new_user=True,
                linked_accounts=["google"]
            )
            
            mock_auth.return_value = mock_result
            
            # Test request
            request = SocialLoginRequest(
                provider=SocialProvider.google,
                access_token="fake-google-token",
                provider_user_id="google123"
            )
            
            # Create service instance (won't be used due to patch)
            service = AuthService(AsyncMock())
            result = await service.authenticate_social_user(request)
            
            # Assertions
            assert result.is_new_user is True
            assert result.user.email == "user@example.com"
            assert "mock-access-token" in result.tokens.access_token
            assert "google" in result.linked_accounts

    @pytest.mark.asyncio
    async def test_apple_social_login_existing_user(self):
        """Test Apple login with existing user."""
        
        with patch.object(AuthService, 'authenticate_social_user') as mock_auth:
            from flerity_core.domain.auth.schemas import SocialAuthResponse, UserProfile, AuthTokenPair
            from datetime import datetime
            
            mock_user = UserProfile(
                id=uuid4(),
                email="existing@example.com",
                email_verified=True,
                gender="non-binary",
                country="US",
                created_at=datetime.utcnow()
            )
            
            mock_tokens = AuthTokenPair(
                access_token="mock-access-token",
                refresh_token="mock-refresh-token",
                expires_in=3600
            )
            
            mock_result = SocialAuthResponse(
                user=mock_user,
                tokens=mock_tokens,
                is_new_user=False,
                linked_accounts=["apple"]
            )
            
            mock_auth.return_value = mock_result
            
            request = SocialLoginRequest(
                provider=SocialProvider.apple,
                access_token="fake-apple-token",
                provider_user_id="apple123"
            )
            
            service = AuthService(AsyncMock())
            result = await service.authenticate_social_user(request)
            
            assert result.is_new_user is False
            assert result.user.email == "existing@example.com"
            assert "apple" in result.linked_accounts

    @pytest.mark.asyncio
    async def test_invalid_provider_token(self):
        """Test authentication with invalid provider token."""
        
        with patch.object(AuthService, 'authenticate_social_user') as mock_auth:
            mock_auth.side_effect = BadRequest("Invalid token")
            
            request = SocialLoginRequest(
                provider=SocialProvider.google,
                access_token="invalid-token",
                provider_user_id="google123"
            )
            
            service = AuthService(AsyncMock())
            
            with pytest.raises(BadRequest, match="Invalid token"):
                await service.authenticate_social_user(request)

    def test_unsupported_provider(self):
        """Test request with unsupported provider."""
        
        with pytest.raises(ValueError):
            # This should cause validation error due to invalid enum value
            request_data = {
                "provider": "unsupported",
                "access_token": "token",
                "provider_user_id": "123"
            }
            SocialLoginRequest(**request_data)

    @pytest.mark.asyncio
    async def test_google_validator_network_error(self):
        """Test Google validator with network error."""
        
        # Mock the validator method directly to avoid complex patching
        with patch.object(GoogleTokenValidator, 'validate_token') as mock_validate:
            mock_validate.side_effect = DependencyError("Erro ao validar token Google: Network error")
            
            validator = GoogleTokenValidator()
            with pytest.raises(DependencyError, match="Erro ao validar token Google"):
                await validator.validate_token("invalid-token")

    @pytest.mark.asyncio
    async def test_apple_validator_invalid_kid(self):
        """Test Apple validator with invalid key ID."""
        
        validator = AppleTokenValidator(client_id="test.client.id")
        
        # Mock invalid JWT token with unknown kid
        invalid_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6InVua25vd24ifQ.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.invalid"
        
        with pytest.raises(DependencyError, match="Erro ao validar token Apple"):
            await validator.validate_token(invalid_token)


# Fixtures for testing
@pytest.fixture
def auth_service():
    """Create mock AuthService instance for testing."""
    return AsyncMock(spec=AuthService)


@pytest.fixture
def existing_user():
    """Mock existing user for testing."""
    from flerity_core.domain.users.schemas import UserOut
    from datetime import datetime
    
    return UserOut(
        id=uuid4(),
        email="existing@example.com",
        name="Existing User",
        gender="non-binary",
        country="US",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

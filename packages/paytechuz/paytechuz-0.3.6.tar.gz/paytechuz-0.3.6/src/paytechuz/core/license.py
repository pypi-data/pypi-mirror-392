"""
License validation and API key verification module.
"""
import os
import hashlib
import time
from typing import Optional, Dict, Any

from .exceptions import AuthenticationError
from .http import HttpClient
from .protection import verify_installation, get_machine_id


class LicenseValidator:
    """
    Validates API keys and manages license verification.
    """
    
    _instance = None
    _cache: Dict[str, Dict[str, Any]] = {}
    _cache_ttl = 3600  # 1 hour cache
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LicenseValidator, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.validation_url = os.getenv(
            "PAYTECHUZ_VALIDATION_URL",
            "https://api.pay-tech.uz"
        )
        self.http_client = HttpClient(
            base_url=self.validation_url,
            timeout=10
        )
    
    def _generate_signature(self, api_key: str, timestamp: int) -> str:
        """
        Generate signature for API key validation.
        
        Args:
            api_key: The API key to validate
            timestamp: Current timestamp
            
        Returns:
            Generated signature
        """
        message = f"{api_key}:{timestamp}"
        return hashlib.sha256(message.encode()).hexdigest()
    
    def _is_cache_valid(self, api_key: str) -> bool:
        """
        Check if cached validation is still valid.
        
        Args:
            api_key: The API key to check
            
        Returns:
            True if cache is valid, False otherwise
        """
        if api_key not in self._cache:
            return False
        
        cache_entry = self._cache[api_key]
        cache_time = cache_entry.get('timestamp', 0)
        
        return (time.time() - cache_time) < self._cache_ttl
    
    def _validate_format(self, api_key: str) -> bool:
        """
        Validate API key format.
        
        Args:
            api_key: The API key to validate
            
        Returns:
            True if format is valid, False otherwise
        """
        if not api_key or not isinstance(api_key, str):
            return False
        
        # API key should be at least 32 characters
        if len(api_key) < 32:
            return False
        
        # Should start with 'ptuz_' prefix
        if not api_key.startswith('ptuz_'):
            return False
        
        return True
    
    def _validate_online(self, api_key: str) -> Dict[str, Any]:
        """
        Validate API key with online service.

        Args:
            api_key: The API key to validate

        Returns:
            Validation result

        Raises:
            AuthenticationError: If validation fails
        """
        try:
            # Verify installation integrity
            if not verify_installation():
                raise AuthenticationError(
                    "Invalid library installation. "
                    "Please reinstall: pip install --upgrade paytechuz"
                )

            timestamp = int(time.time())
            signature = self._generate_signature(api_key, timestamp)
            machine_id = get_machine_id()

            headers = {
                'X-API-Key': api_key,
                'X-Timestamp': str(timestamp),
                'X-Signature': signature,
                'X-Machine-ID': machine_id
            }

            response = self.http_client.get(
                '/v1/license/validate',
                headers=headers
            )

            if response.get('valid'):
                return {
                    'valid': True,
                    'timestamp': time.time(),
                    'features': response.get('features', []),
                    'expires_at': response.get('expires_at')
                }

            return {'valid': False, 'timestamp': time.time()}

        except Exception:
            # If online validation fails, use offline validation
            return self._validate_offline(api_key)
    
    def _validate_offline(self, api_key: str) -> Dict[str, Any]:
        """
        Offline validation using embedded logic.
        
        Args:
            api_key: The API key to validate
            
        Returns:
            Validation result
        """
        # Basic offline validation
        if not self._validate_format(api_key):
            return {'valid': False, 'timestamp': time.time()}
        
        # Extract key parts
        parts = api_key.split('_')
        if len(parts) < 3:
            return {'valid': False, 'timestamp': time.time()}
        
        # Validate checksum
        key_body = '_'.join(parts[:-1])
        checksum = parts[-1]
        
        expected_checksum = hashlib.md5(key_body.encode()).hexdigest()[:8]
        
        if checksum != expected_checksum:
            return {'valid': False, 'timestamp': time.time()}
        
        return {
            'valid': True,
            'timestamp': time.time(),
            'features': ['basic'],
            'expires_at': None
        }
    
    def validate(self, api_key: str, force_online: bool = False) -> bool:
        """
        Validate API key.
        
        Args:
            api_key: The API key to validate
            force_online: Force online validation even if cache is valid
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            AuthenticationError: If API key is invalid
        """
        if not api_key:
            raise AuthenticationError(
                "API key is required. Please set PAYTECHUZ_API_KEY in your settings."
            )
        
        # Check cache first
        if not force_online and self._is_cache_valid(api_key):
            return self._cache[api_key].get('valid', False)
        
        # Validate format first
        if not self._validate_format(api_key):
            raise AuthenticationError(
                "Invalid API key format. API key should start with 'ptuz_' "
                "and be at least 32 characters long."
            )
        
        # Try online validation first, fallback to offline
        try:
            result = self._validate_online(api_key)
        except Exception:
            result = self._validate_offline(api_key)
        
        # Cache the result
        self._cache[api_key] = result
        
        if not result.get('valid'):
            raise AuthenticationError(
                "Invalid API key. Please check your API key or contact support at "
                "https://pay-tech.uz"
            )
        
        return True
    
    def get_features(self, api_key: str) -> list:
        """
        Get available features for API key.
        
        Args:
            api_key: The API key
            
        Returns:
            List of available features
        """
        if api_key in self._cache:
            return self._cache[api_key].get('features', [])
        
        return []
    
    def clear_cache(self, api_key: Optional[str] = None):
        """
        Clear validation cache.
        
        Args:
            api_key: Specific API key to clear, or None to clear all
        """
        if api_key:
            self._cache.pop(api_key, None)
        else:
            self._cache.clear()


# Global validator instance
_validator = LicenseValidator()


def validate_api_key(api_key: str, force_online: bool = False) -> bool:
    """
    Validate API key using global validator.
    
    Args:
        api_key: The API key to validate
        force_online: Force online validation
        
    Returns:
        True if valid
        
    Raises:
        AuthenticationError: If API key is invalid
    """
    return _validator.validate(api_key, force_online)


def get_api_key_features(api_key: str) -> list:
    """
    Get features available for API key.
    
    Args:
        api_key: The API key
        
    Returns:
        List of features
    """
    return _validator.get_features(api_key)


def require_api_key(api_key: Optional[str]) -> str:
    """
    Require API key to be present and valid.
    
    Args:
        api_key: The API key to validate
        
    Returns:
        The validated API key
        
    Raises:
        AuthenticationError: If API key is missing or invalid
    """
    if not api_key:
        # Try to get from environment
        api_key = os.getenv('PAYTECHUZ_API_KEY')
    
    if not api_key:
        raise AuthenticationError(
            "API key is required. Please provide api_key parameter or set "
            "PAYTECHUZ_API_KEY environment variable. "
            "Get your API key at https://pay-tech.uz"
        )
    
    validate_api_key(api_key)
    return api_key


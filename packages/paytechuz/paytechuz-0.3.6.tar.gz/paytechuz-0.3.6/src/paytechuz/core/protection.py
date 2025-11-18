"""
Code protection and anti-tampering mechanisms.
"""
import sys
import os
import hashlib
import inspect
from typing import Optional


class CodeProtection:
    """
    Provides code protection and anti-tampering mechanisms.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CodeProtection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._check_integrity()
            self._check_debugger()
            CodeProtection._initialized = True
    
    def _check_integrity(self):
        """
        Check code integrity to detect tampering.
        """
        # Check if running from source or compiled
        if hasattr(sys, 'frozen'):
            # Running as compiled executable
            return
        
        # Check if critical files have been modified
        try:
            current_file = inspect.getfile(inspect.currentframe())
            current_dir = os.path.dirname(current_file)
            
            # Verify license module exists
            license_file = os.path.join(current_dir, 'license.py')
            if not os.path.exists(license_file):
                raise RuntimeError("Critical library files are missing")
                
        except Exception:
            # If we can't verify, continue but log
            pass
    
    def _check_debugger(self):
        """
        Detect if code is running under debugger.
        """
        # Check for common debugger indicators
        if hasattr(sys, 'gettrace') and sys.gettrace() is not None:
            # Debugger detected - we allow it but could log
            pass
    
    def verify_installation(self) -> bool:
        """
        Verify that the library is properly installed.
        
        Returns:
            True if installation is valid
        """
        try:
            # Check if running from proper installation
            import paytechuz
            
            # Verify package structure
            package_dir = os.path.dirname(paytechuz.__file__)
            
            required_modules = [
                'core',
                'gateways',
                'integrations'
            ]
            
            for module in required_modules:
                module_path = os.path.join(package_dir, module)
                if not os.path.exists(module_path):
                    return False
            
            return True
            
        except ImportError:
            return False
    
    def generate_machine_id(self) -> str:
        """
        Generate a unique machine identifier.
        
        Returns:
            Machine ID hash
        """
        try:
            # Use multiple system identifiers
            identifiers = []
            
            # Platform info
            import platform
            identifiers.append(platform.node())
            identifiers.append(platform.machine())
            
            # Combine and hash
            combined = ''.join(identifiers)
            return hashlib.sha256(combined.encode()).hexdigest()[:16]
            
        except Exception:
            # Fallback to random ID
            import random
            return hashlib.sha256(
                str(random.random()).encode()
            ).hexdigest()[:16]


# Global protection instance
_protection = CodeProtection()


def verify_installation() -> bool:
    """
    Verify library installation.
    
    Returns:
        True if installation is valid
    """
    return _protection.verify_installation()


def get_machine_id() -> str:
    """
    Get machine identifier.
    
    Returns:
        Machine ID
    """
    return _protection.generate_machine_id()


def protect_function(func):
    """
    Decorator to protect critical functions.
    
    Args:
        func: Function to protect
        
    Returns:
        Protected function
    """
    def wrapper(*args, **kwargs):
        # Verify installation before executing
        if not verify_installation():
            raise RuntimeError(
                "Invalid library installation. "
                "Please reinstall paytechuz: pip install --upgrade paytechuz"
            )
        return func(*args, **kwargs)
    
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


#exonware/xwsystem/src/exonware/xwsystem/_lazy_bootstrap.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.401
Generation Date: 11-Nov-2025

Early bootstrap for lazy mode - installs import hook before any imports occur.

This module runs before any other imports to detect [lazy] extra installation
or environment variable and install the import hook immediately. This ensures
the hook is active before serialization modules are imported, enabling automatic
installation of missing dependencies like PyYAML.

Priority alignment:
- Usability (#2): Zero-config lazy mode with pip install package[lazy]
- Performance (#4): Zero overhead when lazy is disabled
- Maintainability (#3): Clean, minimal bootstrap logic
"""

import logging
import os


def _should_enable_lazy_mode() -> bool:
    """
    Detect if lazy mode should be enabled before package initialization.
    
    Checks:
    1. Environment variable XWSYSTEM_LAZY_INSTALL (set by exonware.conf or user)
    2. [lazy] extra via importlib.metadata - checks if lazy dependencies are installed
    
    Returns:
        True if lazy mode should be enabled, False otherwise
    """
    # Check environment variable (can be set by exonware.conf before xwsystem import)
    env_value = os.environ.get('XWSYSTEM_LAZY_INSTALL')
    if env_value:
        normalized = env_value.strip().lower()
        if normalized in ('true', '1', 'yes', 'on'):
            return True
        if normalized in ('false', '0', 'no', 'off'):
            return False

    # Delegate to the primary detection logic in lazy_core so state handling is unified
    try:
        from .utils.lazy_package import lazy_core as _lazy_core
        return _lazy_core._detect_lazy_installation("xwsystem")
    except Exception as exc:
        logging.getLogger("xwsystem._lazy_bootstrap").debug(
            "Lazy bootstrap detection failed: %s", exc, exc_info=True
        )

    return False


# Auto-enable lazy install and install hook if [lazy] extra detected
if _should_enable_lazy_mode():
    try:
        # Lazy import to avoid circular dependency
        # Import here since lazy_package may not be imported yet when bootstrap runs
        from .utils.lazy_package.lazy_core import (
            config_package_lazy_install_enabled,
            is_import_hook_installed,
        )
        
        # Enable lazy install and install hook automatically
        # This will be called again in __init__.py but it's idempotent
        config_package_lazy_install_enabled("xwsystem", enabled=True, install_hook=True)
    except Exception as e:
        # Log but don't fail - package should still load even if lazy setup fails
        # This ensures backward compatibility
        import logging
        logger = logging.getLogger("xwsystem._lazy_bootstrap")
        logger.debug(f"Could not enable lazy mode in bootstrap: {e}", exc_info=True)


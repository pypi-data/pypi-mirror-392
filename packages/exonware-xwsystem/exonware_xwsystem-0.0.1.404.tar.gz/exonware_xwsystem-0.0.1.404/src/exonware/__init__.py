"""
exonware package - Enterprise-grade Python framework ecosystem

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.404
Generation Date: September 04, 2025

This is a namespace package allowing multiple exonware subpackages
to coexist (xwsystem, xwnode, xwdata, etc.)
"""

# Make this a namespace package
__path__ = __import__('pkgutil').extend_path(__path__, __name__)

# Only import version if xwsystem is available (lazy import)
# Root cause: Previous implementation used a hardcoded fallback ("0.0.0"),
# which violates version centralization (GUIDE_DEV / GUIDE_TEST). Fix by
# requiring the centralized version module to load successfully.
try:
    from .xwsystem.version import __version__
except ImportError as exc:  # pragma: no cover - ensure failure is explicit
    raise ImportError(
        "exonware.xwsystem version metadata unavailable. Ensure the package is "
        "installed with its source tree intact so that 'xwsystem.version' can be imported."
    ) from exc

__author__ = 'Eng. Muhammad AlShehri'
__email__ = 'connect@exonware.com'
__company__ = 'eXonware.com'

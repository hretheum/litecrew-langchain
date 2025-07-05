"""LiteCrew API endpoints - Re-export from api package."""


# Re-export create_app from the api package for backward compatibility
def create_app():
    """Create and configure FastAPI application."""
    try:
        # Try relative import first
        from .api import create_app as _create_app

        return _create_app()
    except ImportError:
        # Fallback to absolute import
        from litecrew.api import create_app as _create_app

        return _create_app()


__all__ = ["create_app"]

"""Share link functionality for process configurations."""

import base64
import json
import uuid
from typing import Any, Dict, Optional


class ShareLinkManager:
    """Manage shareable links for process configurations."""

    def __init__(self):
        self.links = {}  # In-memory storage for demo

    def create_share_link(self, config: Dict[str, Any], base_url: str = "") -> str:
        """
        Create a shareable link for a process configuration.

        Args:
            config: Process configuration
            base_url: Base URL for the application

        Returns:
            Shareable URL
        """
        # Generate a short ID
        link_id = str(uuid.uuid4())[:8]

        # Store configuration
        self.links[link_id] = {
            "config": config,
            "created_at": str(uuid.uuid4()),  # Mock timestamp
            "uses": 0,
        }

        # Create URL
        return f"{base_url}/#/shared/{link_id}"

    def create_embedded_link(self, config: Dict[str, Any], base_url: str = "") -> str:
        """
        Create a link with configuration embedded in the URL.

        Args:
            config: Process configuration
            base_url: Base URL for the application

        Returns:
            URL with embedded configuration
        """
        # Encode configuration in URL
        config_json = json.dumps(config, separators=(",", ":"))
        encoded_config = base64.urlsafe_b64encode(config_json.encode()).decode()

        return f"{base_url}/#/config/{encoded_config}"

    def get_config_from_link(self, link_id: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration from a share link ID.

        Args:
            link_id: Share link identifier

        Returns:
            Configuration dict or None if not found
        """
        if link_id in self.links:
            self.links[link_id]["uses"] += 1
            return self.links[link_id]["config"]
        return None

    def get_config_from_embedded(self, encoded_config: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration from embedded link.

        Args:
            encoded_config: Base64 encoded configuration

        Returns:
            Configuration dict or None if invalid
        """
        try:
            # Decode configuration
            config_json = base64.urlsafe_b64decode(encoded_config.encode()).decode()
            return json.loads(config_json)
        except Exception:
            return None

    def list_shared_links(self) -> Dict[str, Dict[str, Any]]:
        """List all shared links with metadata."""
        return self.links

    def delete_link(self, link_id: str) -> bool:
        """Delete a shared link."""
        if link_id in self.links:
            del self.links[link_id]
            return True
        return False


# Global instance
_share_manager: Optional[ShareLinkManager] = None


def get_share_manager() -> ShareLinkManager:
    """Get the global share link manager instance."""
    global _share_manager
    if _share_manager is None:
        _share_manager = ShareLinkManager()
    return _share_manager

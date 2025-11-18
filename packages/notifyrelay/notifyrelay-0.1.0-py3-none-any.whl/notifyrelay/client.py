"""
NotifyRelay client for publishing messages and creating subscribers.
"""

import requests
from typing import Optional
from .subscriber import Subscriber
from .exceptions import AuthenticationError, ConnectionError, NotifyRelayError


class NotifyRelayClient:
    """
    Client for interacting with NotifyRelay service.
    
    Args:
        base_url: Base URL of the NotifyRelay service (e.g., "https://your-app.herokuapp.com")
        publish_key: Optional authentication key for publishing messages
        subscribe_key: Optional authentication key for subscribing to messages
    """
    
    def __init__(
        self,
        base_url: str,
        publish_key: Optional[str] = None,
        subscribe_key: Optional[str] = None
    ):
        self.base_url = base_url.rstrip('/')
        self.publish_key = publish_key
        self.subscribe_key = subscribe_key
    
    def publish(self, topic: str, message: str) -> dict:
        """
        Publish a message to a topic.
        
        Args:
            topic: Topic name to publish to
            message: Message content (opaque string)
            
        Returns:
            dict: Response from server with 'success' and 'messageId' fields
            
        Raises:
            AuthenticationError: If authentication fails
            ConnectionError: If connection to server fails
            NotifyRelayError: For other errors
        """
        if not self.publish_key:
            raise NotifyRelayError("publish_key not configured")
        
        url = f"{self.base_url}/publish"
        headers = {
            "Authorization": self.publish_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "topic": topic,
            "message": message
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 401:
                raise AuthenticationError("Invalid publish key")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 401:
                raise AuthenticationError("Invalid publish key") from e
            raise ConnectionError(f"Failed to publish message: {e}") from e
    
    def create_subscriber(
        self,
        subscriber_id: str,
        subscriber_name: str
    ) -> Subscriber:
        """
        Create a new subscriber instance.
        
        Args:
            subscriber_id: Unique identifier for this subscriber
            subscriber_name: Human-readable name for this subscriber
            
        Returns:
            Subscriber: A new subscriber instance
            
        Raises:
            NotifyRelayError: If subscribe_key not configured
        """
        if not self.subscribe_key:
            raise NotifyRelayError("subscribe_key not configured")
        
        return Subscriber(
            base_url=self.base_url,
            subscribe_key=self.subscribe_key,
            subscriber_id=subscriber_id,
            subscriber_name=subscriber_name
        )
    
    def get_status(self) -> dict:
        """
        Get server status and health information.
        
        Returns:
            dict: Server status including service name, uptime, and stats
        """
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to get status: {e}") from e
    
    def get_subscribers(self) -> list:
        """
        Get list of active subscribers.
        
        Returns:
            list: List of active subscriber information
        """
        try:
            response = requests.get(f"{self.base_url}/subscribers", timeout=5)
            response.raise_for_status()
            return response.json().get("subscribers", [])
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to get subscribers: {e}") from e

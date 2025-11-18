"""
Subscriber for receiving messages from NotifyRelay service.
"""

import json
import queue
import threading
import time
import requests
from typing import List, Optional, Dict, Any
from .exceptions import AuthenticationError, ConnectionError as NotifyRelayConnectionError


class Subscriber:
    """
    Subscriber that polls for messages in a background thread and stores them in a queue.
    
    The main application loop can call get_messages() to retrieve messages at its own pace.
    
    Args:
        base_url: Base URL of the NotifyRelay service
        subscribe_key: Authentication key for subscribing
        subscriber_id: Unique identifier for this subscriber
        subscriber_name: Human-readable name for this subscriber
        poll_timeout: Timeout for long polling in milliseconds (default: 55000)
    """
    
    def __init__(
        self,
        base_url: str,
        subscribe_key: str,
        subscriber_id: str,
        subscriber_name: str,
        poll_timeout: int = 55000
    ):
        self.base_url = base_url.rstrip('/')
        self.subscribe_key = subscribe_key
        self.subscriber_id = subscriber_id
        self.subscriber_name = subscriber_name
        self.poll_timeout = min(poll_timeout, 55000)
        
        self._topics: List[str] = []
        self._json_topics: set = set()  # Topics that should be JSON-parsed
        self._message_queue: queue.Queue = queue.Queue()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        # Error handling
        self._consecutive_errors = 0
        self._max_backoff = 30  # Maximum backoff in seconds
    
    def subscribe(self, topics: List[str], json_mode: bool = False):
        """
        Set the topics to subscribe to.
        
        Args:
            topics: List of topic names to subscribe to
            json_mode: If True, automatically parse message content as JSON
        """
        with self._lock:
            self._topics = list(topics)
            if json_mode:
                self._json_topics.update(topics)
            else:
                # Remove topics from json set if json_mode is False
                self._json_topics.difference_update(topics)
    
    def add_topics(self, topics: List[str], json_mode: bool = False):
        """
        Add additional topics to subscribe to.
        
        Args:
            topics: List of topic names to add
            json_mode: If True, automatically parse message content as JSON for these topics
        """
        with self._lock:
            for topic in topics:
                if topic not in self._topics:
                    self._topics.append(topic)
            if json_mode:
                self._json_topics.update(topics)
    
    def remove_topics(self, topics: List[str]):
        """
        Remove topics from subscription.
        
        Args:
            topics: List of topic names to remove
        """
        with self._lock:
            for topic in topics:
                if topic in self._topics:
                    self._topics.remove(topic)
                if topic in self._json_topics:
                    self._json_topics.remove(topic)
    
    def start(self):
        """
        Start the background polling thread.
        """
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """
        Stop the background polling thread.
        """
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
    
    def is_running(self) -> bool:
        """
        Check if the subscriber is currently running.
        
        Returns:
            bool: True if running, False otherwise
        """
        return self._running
    
    def get_messages(self, topic: Optional[str] = None, block: bool = False, timeout: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Get all pending messages from the queue.
        
        Args:
            topic: Optional topic filter. If provided, only return messages for this topic
            block: If True, block until at least one message is available
            timeout: Maximum time to wait for messages when block=True (None for infinite)
        
        Returns:
            List of message dictionaries with 'topic', 'message', 'timestamp', and 'received_at' fields
        """
        messages = []
        
        if block:
            # Wait for at least one message
            try:
                first_msg = self._message_queue.get(block=True, timeout=timeout)
                if topic is None or first_msg['topic'] == topic:
                    messages.append(first_msg)
            except queue.Empty:
                return messages
        
        # Get all remaining messages (non-blocking)
        while True:
            try:
                msg = self._message_queue.get_nowait()
                if topic is None or msg['topic'] == topic:
                    messages.append(msg)
            except queue.Empty:
                break
        
        return messages
    
    def peek_messages(self, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        View pending messages without removing them from the queue.
        
        Args:
            topic: Optional topic filter
            
        Returns:
            List of message dictionaries
        """
        # Get messages
        messages = self.get_messages(topic=topic)
        
        # Put them back
        for msg in messages:
            self._message_queue.put(msg)
        
        return messages
    
    def clear_messages(self):
        """
        Clear all pending messages from the queue.
        """
        while True:
            try:
                self._message_queue.get_nowait()
            except queue.Empty:
                break
    
    def queue_size(self) -> int:
        """
        Get the number of messages currently in the queue.
        
        Returns:
            int: Number of pending messages
        """
        return self._message_queue.qsize()
    
    def _poll_loop(self):
        """
        Background thread that continuously polls for messages.
        """
        while self._running:
            try:
                # Get current topics
                with self._lock:
                    topics = list(self._topics)
                
                if not topics:
                    # No topics to poll, wait a bit
                    time.sleep(1)
                    continue
                
                # Poll for messages
                messages = self._poll_once(topics)
                
                # Process and enqueue messages
                if messages:
                    self._consecutive_errors = 0
                    for topic, topic_messages in messages.items():
                        for msg_data in topic_messages:
                            message_content = msg_data['message']
                            
                            # Parse JSON if this topic is configured for it
                            if topic in self._json_topics:
                                try:
                                    message_content = json.loads(message_content)
                                except json.JSONDecodeError as e:
                                    # Store error information with the message
                                    message_content = {
                                        '_json_parse_error': str(e),
                                        '_raw_message': message_content
                                    }
                            
                            # Enqueue the message
                            self._message_queue.put({
                                'topic': topic,
                                'message': message_content,
                                'timestamp': msg_data['timestamp'],
                                'received_at': time.time()
                            })
                
            except AuthenticationError:
                # Authentication errors are fatal, stop the thread
                self._running = False
                raise
            
            except Exception as e:
                # Handle connection errors with exponential backoff
                self._consecutive_errors += 1
                backoff = min(2 ** self._consecutive_errors, self._max_backoff)
                time.sleep(backoff)
                
                # Continue loop
                continue
    
    def _poll_once(self, topics: List[str]) -> Optional[Dict[str, List[Dict]]]:
        """
        Perform a single poll request.
        
        Args:
            topics: List of topics to poll for
            
        Returns:
            Dictionary mapping topics to lists of messages, or None on timeout
            
        Raises:
            AuthenticationError: If authentication fails
            NotifyRelayConnectionError: If connection fails
        """
        url = f"{self.base_url}/poll"
        headers = {
            "Authorization": self.subscribe_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "subscriber_id": self.subscriber_id,
            "subscriber_name": self.subscriber_name,
            "topics": topics,
            "timeout": self.poll_timeout
        }
        
        try:
            # Add extra time to request timeout to account for server processing
            request_timeout = (self.poll_timeout / 1000) + 10
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=request_timeout
            )
            
            if response.status_code == 401:
                raise AuthenticationError("Invalid subscribe key")
            
            response.raise_for_status()
            data = response.json()
            
            # Return messages dictionary, or None if no messages
            messages = data.get('messages', {})
            return messages if messages else None
            
        except requests.exceptions.RequestException as e:
            if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 401:
                raise AuthenticationError("Invalid subscribe key") from e
            raise NotifyRelayConnectionError(f"Failed to poll for messages: {e}") from e
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
        return False

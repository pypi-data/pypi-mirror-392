"""
Basic tests for NotifyRelay client.
"""

from urllib import response
import pytest
import time
from notifyrelay import NotifyRelayClient
from notifyrelay.exceptions import NotifyRelayError


def test_client_creation():
    """Test creating a client instance."""
    client = NotifyRelayClient(
        base_url="http://localhost:3000",
        publish_key="test-publish-key",
        subscribe_key="test-subscribe-key"
    )
    
    assert client.base_url == "http://localhost:3000"
    assert client.publish_key == "test-publish-key"
    assert client.subscribe_key == "test-subscribe-key"


def test_client_url_strip_trailing_slash():
    """Test that trailing slashes are removed from base_url."""
    client = NotifyRelayClient(
        base_url="http://localhost:3000/",
        subscribe_key="test-subscribe-key"
    )
    
    assert client.base_url == "http://localhost:3000"


def test_create_subscriber():
    """Test creating a subscriber."""
    client = NotifyRelayClient(
        base_url="http://localhost:3000",
        subscribe_key="test-subscribe-key"
    )
    
    subscriber = client.create_subscriber("test-id", "test-name")
    
    assert subscriber.subscriber_id == "test-id"
    assert subscriber.subscriber_name == "test-name"
    assert subscriber.base_url == "http://localhost:3000"


def test_create_subscriber_without_key():
    """Test that creating a subscriber without subscribe_key raises error."""
    client = NotifyRelayClient(base_url="http://localhost:3000")
    
    with pytest.raises(NotifyRelayError, match="subscribe_key not configured"):
        client.create_subscriber("test-id", "test-name")


def test_subscriber_topic_management():
    """Test adding and removing topics."""
    client = NotifyRelayClient(
        base_url="http://localhost:3000",
        subscribe_key="test-subscribe-key"
    )
    
    subscriber = client.create_subscriber("test-id", "test-name")
    
    # Subscribe to topics
    subscriber.subscribe(["topic1", "topic2"])
    assert set(subscriber._topics) == {"topic1", "topic2"}
    
    # Add topics
    subscriber.add_topics(["topic3"])
    assert set(subscriber._topics) == {"topic1", "topic2", "topic3"}
    
    # Remove topics
    subscriber.remove_topics(["topic2"])
    assert set(subscriber._topics) == {"topic1", "topic3"}


def test_subscriber_json_mode():
    """Test JSON mode topic tracking."""
    client = NotifyRelayClient(
        base_url="http://localhost:3000",
        subscribe_key="test-subscribe-key"
    )
    
    subscriber = client.create_subscriber("test-id", "test-name")
    
    # Subscribe with JSON mode
    subscriber.subscribe(["json-topic"], json_mode=True)
    assert "json-topic" in subscriber._json_topics
    
    # Add non-JSON topic
    subscriber.add_topics(["string-topic"], json_mode=False)
    assert "string-topic" not in subscriber._json_topics
    assert "json-topic" in subscriber._json_topics


def test_subscriber_lifecycle():
    """Test subscriber start/stop."""
    client = NotifyRelayClient(
        base_url="http://localhost:3000",
        subscribe_key="test-subscribe-key"
    )
    
    subscriber = client.create_subscriber("test-id", "test-name")
    subscriber.subscribe(["test-topic"])
    
    # Initially not running
    assert not subscriber.is_running()
    
    # Start subscriber
    subscriber.start()
    assert subscriber.is_running()
    
    # Stop subscriber
    subscriber.stop()
    time.sleep(0.5)  # Give thread time to stop
    assert not subscriber.is_running()


def test_subscriber_context_manager():
    """Test subscriber as context manager."""
    client = NotifyRelayClient(
        base_url="http://localhost:3000",
        subscribe_key="test-subscribe-key"
    )
    
    subscriber = client.create_subscriber("test-id", "test-name")
    subscriber.subscribe(["test-topic"])
    
    assert not subscriber.is_running()
    
    with subscriber:
        # Should be running inside context
        assert subscriber.is_running()
    
    # Should be stopped after context
    time.sleep(0.5)
    assert not subscriber.is_running()


def test_message_queue_operations():
    """Test message queue operations."""
    client = NotifyRelayClient(
        base_url="http://localhost:3000",
        subscribe_key="test-subscribe-key"
    )
    
    subscriber = client.create_subscriber("test-id", "test-name")
    
    # Initially empty
    assert subscriber.queue_size() == 0
    
    # Manually add messages for testing
    subscriber._message_queue.put({
        'topic': 'test',
        'message': 'msg1',
        'timestamp': '2024-01-01T00:00:00.000Z',
        'received_at': time.time()
    })
    subscriber._message_queue.put({
        'topic': 'test',
        'message': 'msg2',
        'timestamp': '2024-01-01T00:00:01.000Z',
        'received_at': time.time()
    })
    
    assert subscriber.queue_size() == 2
    
    # Get messages
    messages = subscriber.get_messages()
    assert len(messages) == 2
    assert subscriber.queue_size() == 0
    
    # Clear messages
    subscriber._message_queue.put({'topic': 'test', 'message': 'msg3', 'timestamp': '', 'received_at': time.time()})
    subscriber.clear_messages()
    assert subscriber.queue_size() == 0


if __name__ == "__main__":
    test_client_creation()
    test_client_url_strip_trailing_slash()
    test_create_subscriber()
    test_create_subscriber_without_key()
    test_subscriber_topic_management()
    test_subscriber_json_mode()
    test_subscriber_lifecycle()
    test_subscriber_context_manager()
    test_message_queue_operations()
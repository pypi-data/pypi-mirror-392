# NotifyRelay Python Client

A Python client library for the [NotifyRelay](https://github.com/magland/notifyrelay) pub/sub messaging service. Provides a queue-based message retrieval system with background polling for seamless integration into Python applications.

## Features

- **Queue-based message retrieval**: Background thread polls for messages, main loop retrieves at its own pace
- **Thread-safe**: All operations are thread-safe for concurrent access
- **Optional JSON deserialization**: Automatic JSON parsing per topic with error handling
- **Topic management**: Dynamic subscription and unsubscription
- **Publisher support**: Simple API for publishing messages
- **Context manager support**: Clean resource management
- **No callbacks required**: Pull-based model gives your application full control

## Installation

### From source

```bash
cd python-client
pip install -e .
```

### From PyPI (when published)

```bash
pip install notifyrelay
```

## Quick Start

### Subscribing to Messages

```python
from notifyrelay import NotifyRelayClient
import time

# Create client
client = NotifyRelayClient(
    base_url="https://your-app.herokuapp.com",
    subscribe_key="your-subscribe-key"
)

# Create subscriber
subscriber = client.create_subscriber(
    subscriber_id="my-unique-id",
    subscriber_name="my-app"
)

# Subscribe to topics
subscriber.subscribe(["alerts", "logs"])

# Start background polling
subscriber.start()

# Main application loop
while True:
    # Do your application work...
    process_data()
    
    # Check for new messages (non-blocking)
    messages = subscriber.get_messages()
    
    for msg in messages:
        print(f"[{msg['topic']}] {msg['message']}")
    
    time.sleep(0.1)

# Clean up
subscriber.stop()
```

### Publishing Messages

```python
from notifyrelay import NotifyRelayClient

client = NotifyRelayClient(
    base_url="https://your-app.herokuapp.com",
    publish_key="your-publish-key"
)

# Publish a message
result = client.publish("alerts", "System alert: High CPU usage")
print(f"Message published with ID: {result['messageId']}")
```

### JSON Messages

```python
import json

# Subscribe with automatic JSON parsing
subscriber.subscribe(["data"], json_mode=True)
subscriber.start()

# Later in your loop...
messages = subscriber.get_messages()
for msg in messages:
    if msg['topic'] == 'data':
        data = msg['message']  # Already parsed as dict/list
        
        # Check for parse errors
        if isinstance(data, dict) and '_json_parse_error' in data:
            print(f"JSON parse error: {data['_json_parse_error']}")
            print(f"Raw message: {data['_raw_message']}")
        else:
            print(f"Received data: {data}")

# Publishing JSON (serialize to string)
client.publish("data", json.dumps({"temperature": 72, "humidity": 45}))
```

## API Reference

### NotifyRelayClient

Main client for interacting with NotifyRelay service.

**Constructor:**
```python
client = NotifyRelayClient(
    base_url: str,
    publish_key: Optional[str] = None,
    subscribe_key: Optional[str] = None
)
```

**Methods:**
- `publish(topic: str, message: str) -> dict`: Publish a message to a topic
- `create_subscriber(subscriber_id: str, subscriber_name: str) -> Subscriber`: Create a new subscriber
- `get_status() -> dict`: Get server status
- `get_subscribers() -> list`: Get list of active subscribers

### Subscriber

Handles message polling and queueing in a background thread.

**Methods:**

- `subscribe(topics: List[str], json_mode: bool = False)`: Set topics to subscribe to
- `add_topics(topics: List[str], json_mode: bool = False)`: Add more topics
- `remove_topics(topics: List[str])`: Remove topics
- `start()`: Start background polling thread
- `stop()`: Stop background polling thread
- `is_running() -> bool`: Check if subscriber is running
- `get_messages(topic: Optional[str] = None, block: bool = False, timeout: Optional[float] = None) -> List[dict]`: Get pending messages
- `peek_messages(topic: Optional[str] = None) -> List[dict]`: View messages without removing
- `clear_messages()`: Clear all pending messages
- `queue_size() -> int`: Get number of pending messages

**Message Format:**
```python
{
    'topic': 'topic-name',
    'message': 'message-content',  # or parsed dict/list if json_mode=True
    'timestamp': '2024-01-01T12:00:00.000Z',  # Server timestamp
    'received_at': 1234567890.123  # Local timestamp when received
}
```

**Context Manager:**
```python
with subscriber:
    # Subscriber automatically starts
    while running:
        messages = subscriber.get_messages()
        process(messages)
# Subscriber automatically stops
```

## Usage Patterns

### Integration with Existing Event Loop

```python
class MyApplication:
    def __init__(self):
        client = NotifyRelayClient(
            base_url=config.NOTIFYRELAY_URL,
            subscribe_key=config.SUBSCRIBE_KEY
        )
        self.subscriber = client.create_subscriber("my-app", "MyApp")
        self.subscriber.subscribe(["commands", "events"])
        self.subscriber.start()
    
    def run(self):
        while self.running:
            # Your application's main work
            self.process_frames()
            self.update_ui()
            
            # Check for relay messages
            messages = self.subscriber.get_messages()
            for msg in messages:
                self.handle_relay_message(msg)
            
            time.sleep(0.016)  # ~60 FPS
    
    def shutdown(self):
        self.subscriber.stop()
```

### Topic-Specific Filtering

```python
# Get only messages for a specific topic
alert_messages = subscriber.get_messages(topic="alerts")

# Process different topics separately
for msg in subscriber.get_messages(topic="logs"):
    logger.log(msg['message'])

for msg in subscriber.get_messages(topic="commands"):
    executor.execute(msg['message'])
```

### Blocking Wait for Messages

```python
# Block until at least one message arrives (with timeout)
messages = subscriber.get_messages(block=True, timeout=5.0)

if messages:
    print(f"Received {len(messages)} messages")
else:
    print("Timeout - no messages received")
```

## Examples

See the `examples/` directory for complete working examples:

- `simple_subscriber.py`: Basic message subscription
- `json_messages.py`: Automatic JSON parsing
- `publisher.py`: Publishing messages

## Error Handling

```python
from notifyrelay import NotifyRelayClient, AuthenticationError, ConnectionError

try:
    client = NotifyRelayClient(base_url=url, publish_key=key)
    client.publish("topic", "message")
except AuthenticationError:
    print("Invalid authentication key")
except ConnectionError:
    print("Failed to connect to server")
```

## Requirements

- Python >= 3.7
- requests >= 2.25.0

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Deploying to PyPI

For maintainers, to publish a new version to PyPI:

1. **Update version**: Increment the version number in both `setup.py` and `pyproject.toml`

2. **Install build tools** (if not already installed):
   ```bash
   pip install --upgrade build twine
   ```

3. **Build the distribution packages**:
   ```bash
   cd python-client
   python -m build
   ```

4. **Upload to PyPI**:
   ```bash
   python -m twine upload dist/*
   ```
   
   You will be prompted for your PyPI username and password (or API token).

5. **Verify the upload**: Check https://pypi.org/project/notifyrelay/ to confirm the new version is available

**Note**: Make sure to clean the `dist/` directory between releases to avoid uploading old versions:
```bash
rm -rf dist/
```

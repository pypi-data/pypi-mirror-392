#!/usr/bin/env python3
"""
JSON message example - demonstrates automatic JSON deserialization.
"""

import time
from notifyrelay import NotifyRelayClient

# Configuration
BASE_URL = "http://localhost:3000"
SUBSCRIBE_KEY = "test-subscribe-key"
SUBSCRIBER_ID = "json-example"
SUBSCRIBER_NAME = "JSON Python Subscriber"

def main():
    # Create client
    client = NotifyRelayClient(
        base_url=BASE_URL,
        subscribe_key=SUBSCRIBE_KEY
    )
    
    # Create subscriber
    subscriber = client.create_subscriber(
        subscriber_id=SUBSCRIBER_ID,
        subscriber_name=SUBSCRIBER_NAME
    )
    
    # Subscribe to topics with JSON mode enabled
    subscriber.subscribe(["data", "events"], json_mode=True)
    
    # Also subscribe to some raw string topics
    subscriber.add_topics(["logs"], json_mode=False)
    
    # Start background polling
    subscriber.start()
    print(f"Subscriber started. Listening for messages...")
    print("  - data, events (JSON mode)")
    print("  - logs (raw strings)")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        # Main application loop
        while True:
            # Do your application work here...
            time.sleep(1)
            
            # Check for new messages
            messages = subscriber.get_messages()
            
            for msg in messages:
                topic = msg['topic']
                message = msg['message']
                timestamp = msg['timestamp']
                
                # Handle based on topic
                if topic in ["data", "events"]:
                    # Message is automatically parsed as JSON
                    if isinstance(message, dict):
                        if '_json_parse_error' in message:
                            # JSON parsing failed
                            print(f"  [{topic}] JSON Parse Error: {message['_json_parse_error']}")
                            print(f"         Raw: {message['_raw_message']}")
                        else:
                            # Successfully parsed JSON
                            print(f"  [{topic}] JSON: {message}")
                    else:
                        print(f"  [{topic}] {message}")
                
                elif topic == "logs":
                    # Raw string message
                    print(f"  [{topic}] {message}")
            
    except KeyboardInterrupt:
        print("\n\nStopping subscriber...")
        subscriber.stop()
        print("Subscriber stopped.")

if __name__ == "__main__":
    main()

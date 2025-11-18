#!/usr/bin/env python3
"""
Simple subscriber example - demonstrates basic message retrieval.
"""

import time
from notifyrelay import NotifyRelayClient

# Configuration
BASE_URL = "http://localhost:3000"
SUBSCRIBE_KEY = "test-subscribe-key"
SUBSCRIBER_ID = "simple-example"
SUBSCRIBER_NAME = "Simple Python Subscriber"

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
    
    # Subscribe to topics
    subscriber.subscribe(["alerts", "logs"])
    
    # Start background polling
    subscriber.start()
    print(f"Subscriber started. Listening for messages on topics: alerts, logs")
    print("Press Ctrl+C to stop\n")
    
    try:
        # Main application loop
        while True:
            # Do your application work here...
            time.sleep(2)
            
            # Check for new messages (non-blocking)
            messages = subscriber.get_messages()
            
            if messages:
                print(f"\nReceived {len(messages)} message(s):")
                for msg in messages:
                    topic = msg['topic']
                    message = msg['message']
                    timestamp = msg['timestamp']
                    print(f"  [{topic}] {message} (at {timestamp})")
            
    except KeyboardInterrupt:
        print("\n\nStopping subscriber...")
        subscriber.stop()
        print("Subscriber stopped.")

if __name__ == "__main__":
    main()

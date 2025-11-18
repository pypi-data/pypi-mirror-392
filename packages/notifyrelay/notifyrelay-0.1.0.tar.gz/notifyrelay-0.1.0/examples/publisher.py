#!/usr/bin/env python3
"""
Publisher example - demonstrates publishing messages to topics.
"""

import json
import time
from notifyrelay import NotifyRelayClient

# Configuration
BASE_URL = "http://localhost:3000"
PUBLISH_KEY = "test-publish-key"

def main():
    # Create client
    client = NotifyRelayClient(
        base_url=BASE_URL,
        publish_key=PUBLISH_KEY
    )
    
    print("Publishing messages to NotifyRelay...")
    print("Press Ctrl+C to stop\n")
    
    try:
        count = 0
        while True:
            count += 1
            
            # Publish a simple string message
            result = client.publish("alerts", f"Alert message #{count}")
            print(f"Published to 'alerts': message_id={result['messageId']}")
            
            # Publish a JSON message (as a string)
            data = {
                "count": count,
                "timestamp": time.time(),
                "value": count * 10
            }
            result = client.publish("data", json.dumps(data))
            print(f"Published to 'data': message_id={result['messageId']}")
            
            # Publish a log message
            result = client.publish("logs", f"Log entry {count}")
            print(f"Published to 'logs': message_id={result['messageId']}\n")
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nStopped publishing.")

if __name__ == "__main__":
    main()

# Dissectica CDP Python Client

This is the official Python SDK for the Dissectica Customer Data Platform.

The client is asynchronous, thread-safe, and uses a local SQLite database for resilient event batching, ensuring no data is lost during network failures or application crashes.

## Installation

```bash
pip install dissectica-cdp-client
```
## Quick start
```python 

import time
from cdp_client import CDPClient

# 1. Configuration
HOST = "[http://your-producer.example.com](http://your-producer.example.com)"
PROJECT_KEY = "YOUR_PROJECT_KEY"
SCHEMA_LIST = ["user_product_purchase_schema_updated"]

# 2. Initialize the client
# This starts the background flushing thread
client = CDPClient(
    host=HOST,
    project_key=PROJECT_KEY,
    schema_names=SCHEMA_LIST,
    flush_interval=10 # Auto-flush every 10 seconds
)

# 3. Track an event
# This is a fast, non-blocking call.
client.track({
    "user_id": "user-12345",
    "session_id": "session-abc",
    "event_type": "PAGE_VIEW",
    "page_url": "/product/test"
})

# Give the background thread time to send
time.sleep(15)

# 4. Shut down (sends any remaining events)
client.shutdown()
```
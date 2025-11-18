import requests
import json
import base64
import uuid
import io
import time
import atexit
import sqlite3
import threading
import logging
from datetime import datetime, timezone
from avro.schema import parse as parse_schema, Schema
from avro.io import DatumWriter, BinaryEncoder
from typing import List, Dict, Any, Optional, Set, Tuple

# --- SDK Configuration ---
DEFAULT_FLUSH_INTERVAL = 10  # seconds
DEFAULT_BATCH_SIZE = 100
DEFAULT_AUTH_TTL = 15 * 60   # 15 minutes
DEFAULT_SCHEMA_TTL = 60 * 60 # 1 hour
DB_NAME = "dissectica_events.db"
DB_TABLE = "event_queue"

# Configure logging
log = logging.getLogger("CDPClient")
log.setLevel(logging.INFO)
if not log.hasHandlers():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    log.addHandler(handler)


class CDPClient:
    """
    Production-ready Python SDK for your CDP.
    
    Handles multiple schemas, local SQLite persistence, automatic
    batching, JWT refreshing, and schema version caching.
    """

    def __init__(self, host: str, project_key: str, schema_names: List[str],
                 flush_interval: int = DEFAULT_FLUSH_INTERVAL, 
                 batch_size: int = DEFAULT_BATCH_SIZE,
                 auth_ttl: int = DEFAULT_AUTH_TTL,
                 schema_ttl: int = DEFAULT_SCHEMA_TTL):
        
        if not schema_names:
            raise ValueError("schema_names list cannot be empty.")
            
        log.info(f"Initializing CDP Client for host {host}...")
        self.host = host
        self.project_key = project_key
        
        # --- Multi-Schema Setup ---
        self.default_schema_name = schema_names[0]
        self.all_schema_names: Set[str] = set(schema_names)
        self.schema_url_template = f"{host}/schemas/{{schema_name}}"
        log.info(f"Default schema set to: {self.default_schema_name}")
        log.info(f"Tracking enabled for schemas: {', '.join(self.all_schema_names)}")
        
        self.flush_interval = flush_interval
        self.batch_size = batch_size
        self.auth_ttl_seconds = auth_ttl
        self.schema_ttl_seconds = schema_ttl

        # API Endpoints
        self.auth_url = f"{host}/auth/token"
        self.batch_url = f"{host}/events/batch"

        # State management
        self._jwt: Optional[str] = None
        self._jwt_fetched_at: Optional[float] = None
        self._schema_cache: Dict[str, Dict] = {}
        
        self._auth_lock = threading.Lock()
        self._schema_cache_lock = threading.Lock()
        
        # Persistent HTTP session
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})

        # SQLite setup
        self._db_lock = threading.Lock()
        self._init_sqlite()

        # Background flushing thread
        self._running = True
        self._flush_thread = threading.Thread(target=self._run_background_flush, daemon=True)
        self._flush_thread.start()
        log.info("Background flush thread started.")

        atexit.register(self.shutdown)
        log.info("Shutdown hook registered.")

    def _init_sqlite(self):
        """Initializes the local SQLite database and table."""
        try:
            with self._db_lock, sqlite3.connect(DB_NAME) as conn:
                conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {DB_TABLE} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    schema_name TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                log.info(f"Local event database '{DB_NAME}' initialized.")
        except Exception as e:
            log.critical(f"Failed to initialize SQLite: {e}")

    def _get_db_conn(self):
        """Returns a new thread-safe connection to the SQLite DB."""
        return sqlite3.connect(DB_NAME, timeout=10)

    def _ensure_authenticated(self) -> bool:
        """
        Ensures a valid JWT is available, fetching one if it's
        missing or older than 15 minutes.
        """
        now = time.monotonic()
        is_expired = (self._jwt_fetched_at is None) or \
                     (now - self._jwt_fetched_at > self.auth_ttl_seconds)

        if self._jwt and not is_expired:
            return True

        with self._auth_lock:
            now = time.monotonic()
            is_expired = (self._jwt_fetched_at is None) or \
                         (now - self._jwt_fetched_at > self.auth_ttl_seconds)
            
            if self._jwt and not is_expired:
                return True
            
            log.info("🔑 Authenticating with server (token missing or expired)...")
            try:
                response = self._session.post(
                    self.auth_url,
                    headers={
                        "X-Project-Key": self.project_key,
                        "Origin": self.host
                    }
                )
                response.raise_for_status()
                self._jwt = response.json()['token']
                self._jwt_fetched_at = now
                self._session.headers.update({"Authorization": f"Bearer {self._jwt}"})
                log.info("✅ Authentication successful.")
                return True
            except Exception as e:
                log.error(f"❌ Authentication failed: {e}")
                return False

    def _get_or_fetch_schema(self, schema_name: str) -> Optional[Schema]:
        """
        Gets a schema from the cache, or fetches and caches it.
        Handles cache TTL for schema versioning.
        """
        if schema_name not in self.all_schema_names:
            log.error(f"Schema '{schema_name}' is not in the allowed list for this client.")
            return None

        now = time.monotonic()
        
        cached_entry = self._schema_cache.get(schema_name)
        if cached_entry and (now - cached_entry['fetched_at'] < self.schema_ttl_seconds):
            return cached_entry['schema']

        with self._schema_cache_lock:
            cached_entry = self._schema_cache.get(schema_name)
            if cached_entry and (now - cached_entry['fetched_at'] < self.schema_ttl_seconds):
                return cached_entry['schema']

            if not self._ensure_authenticated():
                log.error(f"Cannot load schema '{schema_name}', authentication failed.")
                return None

            log.info(f"Fetching schema '{schema_name}' (missing or expired)...")
            try:
                url = self.schema_url_template.format(schema_name=schema_name)
                response = self._session.get(url)
                response.raise_for_status()
                
                schema_data = response.json()
                
                if 'schema' not in schema_data:
                    log.error(f"❌ Invalid schema response for '{schema_name}': 'schema' key is missing.")
                    return None
                    
                actual_schema_json = schema_data['schema']
                parsed_schema = parse_schema(json.dumps(actual_schema_json))
                
                self._schema_cache[schema_name] = {
                    'schema': parsed_schema,
                    'fetched_at': now
                }
                log.info(f"✅ Avro schema '{schema_name}' loaded and parsed.")
                return parsed_schema
                
            except Exception as e:
                log.error(f"❌ Failed to load schema '{schema_name}': {e}")
                return None

    def track(self, event_data: Dict[str, Any], schema_name: str = None) -> str:
        """
        Tracks a single event.
        
        :param event_data: A Python dict matching the Avro schema.
        :param schema_name: (Optional) The schema to use.
                            If None, uses the default schema.
        :return: The event_id used for this event (for deduplication).
        """
        
        name_to_use = schema_name or self.default_schema_name
        
        if name_to_use not in self.all_schema_names:
            log.error(f"Event tracking failed: Schema '{name_to_use}' is not in the client's allowed list.")
            return ""

        try:
            event_id = event_data.get("event_id", str(uuid.uuid4()))
            event_data["event_id"] = event_id
            event_data["timestamp"] = event_data.get("timestamp", int(datetime.now(timezone.utc).timestamp() * 1000))
            
            payload_json = json.dumps(event_data)
            
            with self._db_lock, self._get_db_conn() as conn:
                conn.execute(
                    f"INSERT INTO {DB_TABLE} (schema_name, payload) VALUES (?, ?)",
                    (name_to_use, payload_json)
                )
                conn.commit()
            
            return event_id
            
        except Exception as e:
            log.error(f"Failed to write event to local queue: {e}")
            return ""

    def flush(self):
        """
        Manually triggers a batch flush.
        Pulls events from SQLite, serializes them, sends to the /events/batch
        endpoint, and deletes successful events from the local DB.
        """
        
        rows = []
        try:
            with self._db_lock, self._get_db_conn() as conn:
                cursor = conn.execute(
                    f"SELECT id, schema_name, payload FROM {DB_TABLE} ORDER BY id ASC LIMIT ?",
                    (self.batch_size,)
                )
                rows = cursor.fetchall()
                if not rows:
                    log.info("Flush: No events to send.")
                    return
        except Exception as e:
            log.error(f"Failed to read from local event queue: {e}")
            return

        if not self._ensure_authenticated():
             log.warning("Flush failed: Client not ready (auth).")
             return
             
        request_body, db_ids_to_send, db_ids_to_delete_as_poison = self._prepare_batch(rows)
        
        if db_ids_to_delete_as_poison:
            log.warning(f"Deleting {len(db_ids_to_delete_as_poison)} poison-pill events that failed serialization.")
            self._delete_events_from_db(db_ids_to_delete_as_poison)
            
        if not request_body["events"]:
            log.info("Flush: No valid events to send after serialization.")
            return

        try:
            log.info(f"Flushing batch of {len(db_ids_to_send)} events...")
            response = self._session.post(self.batch_url, data=json.dumps(request_body))
            response.raise_for_status() 

            successful_db_ids = []
            if response.status_code == 207:
                res_data = response.json()
                statuses = res_data.get('statuses', [])
                log.info(f"✅ Batch sent (207): Processed: {res_data.get('processedCount', 0)}, Failed: {res_data.get('failedCount', 0)}")
                
                for i, status in enumerate(statuses):
                    db_id = db_ids_to_send[i]
                    
                    # --- THIS IS THE FIX ---
                    # Your producer sends "success" (lowercase) on success.
                    if status == "success": 
                        successful_db_ids.append(db_id)
                    else:
                        # It's an error object like: {"error": {"reason": "..."}}
                        # We check if it's a dictionary before calling .get()
                        if isinstance(status, dict):
                            reason = status.get('error', {}).get('reason', 'unknown error')
                            log.warning(f"Event {db_id} failed server validation: {reason}")
                            # This was a bad event, delete it so we don't retry (poison pill)
                            successful_db_ids.append(db_id)
                        else:
                            # Unknown status type
                            log.error(f"Event {db_id} had unknown status: {status}. Will not delete, will retry.")
            
            else:
                log.info(f"✅ Batch sent successfully (Status: {response.status_code})")
                successful_db_ids = db_ids_to_send

            self._delete_events_from_db(successful_db_ids)

        except Exception as e:
            log.error(f"❌ Flush failed: {e}. Events will be retried later.")

    def _prepare_batch(self, rows: List[tuple]) -> Tuple[dict, list, list]:
        """
        Converts a list of DB rows (id, schema_name, payload_json)
        into the Avro-based request body.
        
        Returns: (request_body, db_ids_to_send, db_ids_to_delete_as_poison)
        """
        request_body = {"events": []}
        db_ids_to_send = []
        db_ids_to_delete_as_poison = []
        
        for (db_id, schema_name, payload_json) in rows:
            try:
                avro_schema = self._get_or_fetch_schema(schema_name)
                if not avro_schema:
                    log.warning(f"Skipping event {db_id}, could not load schema '{schema_name}'.")
                    db_ids_to_delete_as_poison.append(db_id)
                    continue
                
                event_data = json.loads(payload_json)
                
                writer = DatumWriter(avro_schema)
                bytes_writer = io.BytesIO()
                encoder = BinaryEncoder(bytes_writer)
                writer.write(event_data, encoder)
                raw_avro_bytes = bytes_writer.getvalue()
                
                b64_payload = base64.b64encode(raw_avro_bytes).decode('utf-8')
                
                request_body["events"].append({
                    "schemaName": schema_name,
                    "payload": b64_payload
                })
                db_ids_to_send.append(db_id)
                
            except Exception as e:
                log.warning(f"Failed to serialize event {db_id} for schema '{schema_name}', marking as poison: {e}")
                db_ids_to_delete_as_poison.append(db_id)
        
        return request_body, db_ids_to_send, db_ids_to_delete_as_poison

    def _delete_events_from_db(self, ids: List[int]):
        """Helper to delete a list of event IDs from SQLite."""
        if not ids:
            return
        try:
            with self._db_lock, self._get_db_conn() as conn:
                id_tuple = tuple(ids)
                if len(id_tuple) == 1:
                    conn.execute(f"DELETE FROM {DB_TABLE} WHERE id = ?", (id_tuple[0],))
                else:
                    placeholders = ', '.join('?' * len(id_tuple))
                    conn.execute(f"DELETE FROM {DB_TABLE} WHERE id IN ({placeholders})", id_tuple)
                conn.commit()
                log.info(f"Deleted {len(ids)} handled events from local DB.")
        except Exception as e:
            log.critical(f"Failed to delete sent events from DB: {e}")

    def _run_background_flush(self):
        """The target function for the background thread."""
        log.info("Background flush thread started.")
        while self._running:
            try:
                time.sleep(self.flush_interval)
                self.flush()
            except Exception as e:
                log.error(f"Error in background flush thread: {e}")
        log.info("Background flush thread stopping.")

    def shutdown(self):
        """Gracefully shuts down the client."""
        log.info("Shutting down CDP client...")
        if self._running:
            self._running = False
            log.info("Waiting for flush thread to stop...")
        
        log.info("Sending final batch...")
        try:
            self.flush()
        except Exception as e:
            log.warning(f"Final flush failed: {e}")
        log.info("CDP Client shut down.")
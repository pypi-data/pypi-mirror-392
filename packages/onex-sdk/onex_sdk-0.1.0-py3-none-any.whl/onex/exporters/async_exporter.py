"""
Async Signal Exporter
Non-blocking signal export to OneX platform
"""

import requests
import threading
import queue
import time
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class AsyncSignalExporter:
    """
    Asynchronous signal exporter
    Exports signals in background thread to avoid blocking inference
    """
    
    def __init__(self, endpoint: str, api_key: str = None, batch_size: int = 10):
        self.endpoint = endpoint
        self.api_key = api_key
        self.batch_size = batch_size
        
        # Signal queue for async processing
        self.signal_queue = queue.Queue(maxsize=1000)
        
        # Start background export thread
        self.running = True
        self.export_thread = threading.Thread(target=self._export_loop, daemon=True)
        self.export_thread.start()
        
        logger.info(f"Signal exporter initialized: {endpoint}")
    
    def export(self, signals: Dict[str, Any]):
        """
        Export signals asynchronously
        Non-blocking - returns immediately
        """
        try:
            self.signal_queue.put_nowait(signals)
        except queue.Full:
            logger.warning("Signal queue full, dropping signal")
    
    def _export_loop(self):
        """Background thread that exports signals"""
        batch = []
        
        while self.running:
            try:
                # Collect signals for batching
                timeout = 1.0  # seconds
                signal = self.signal_queue.get(timeout=timeout)
                batch.append(signal)
                
                # Send batch when full or timeout
                if len(batch) >= self.batch_size:
                    self._send_batch(batch)
                    batch = []
                
            except queue.Empty:
                # Timeout - send whatever we have
                if batch:
                    self._send_batch(batch)
                    batch = []
            
            except Exception as e:
                logger.error(f"Error in export loop: {e}")
    
    def _send_batch(self, batch):
        """Send batch of signals to OneX API"""
        try:
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            response = requests.post(
                self.endpoint,
                json={'signals': batch},
                headers=headers,
                timeout=5.0
            )
            
            if response.status_code == 200:
                logger.debug(f"Exported {len(batch)} signals successfully")
            else:
                logger.warning(f"Export failed: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Failed to export signals: {e}")
    
    def close(self):
        """Stop exporter and cleanup"""
        self.running = False
        self.export_thread.join(timeout=5.0)
        logger.info("Signal exporter stopped")

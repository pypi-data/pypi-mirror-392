# lunalib/core/mempool.py
import time
import requests
import threading
from queue import Queue
from typing import Dict, List, Optional, Set
import json
import hashlib

class MempoolManager:
    """Manages transaction mempool and network broadcasting"""
    
    def __init__(self, network_endpoints: List[str] = None):
        self.network_endpoints = network_endpoints or ["https://bank.linglin.art"]
        self.local_mempool = {}  # {tx_hash: transaction}
        self.pending_broadcasts = Queue()
        self.confirmed_transactions: Set[str] = set()
        self.max_mempool_size = 10000
        self.broadcast_retries = 3
        self.is_running = True
        
        # Start background broadcast thread
        self.broadcast_thread = threading.Thread(target=self._broadcast_worker, daemon=True)
        self.broadcast_thread.start()
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self.cleanup_thread.start()
    
    def add_transaction(self, transaction: Dict) -> bool:
        """Add transaction to local mempool and broadcast to network"""
        try:
            tx_hash = transaction.get('hash')
            if not tx_hash:
                print("DEBUG: Transaction missing hash")
                return False
            
            # Check if transaction already exists or is confirmed
            if tx_hash in self.local_mempool or tx_hash in self.confirmed_transactions:
                print(f"DEBUG: Transaction already processed: {tx_hash}")
                return True
            
            # Validate basic transaction structure
            if not self._validate_transaction_basic(transaction):
                print("DEBUG: Transaction validation failed")
                return False
            
            # Add to local mempool
            self.local_mempool[tx_hash] = {
                'transaction': transaction,
                'timestamp': time.time(),
                'broadcast_attempts': 0,
                'last_broadcast': 0
            }
            print(f"DEBUG: Added transaction to mempool: {tx_hash}")
            
            # Queue for broadcasting
            self.pending_broadcasts.put(transaction)
            print(f"DEBUG: Queued transaction for broadcasting: {tx_hash}")
            
            return True
            
        except Exception as e:
            print(f"DEBUG: Error adding transaction to mempool: {e}")
            return False
    
    def broadcast_transaction(self, transaction: Dict) -> bool:
        """Broadcast transaction to network endpoints"""
        tx_hash = transaction.get('hash')
        print(f"DEBUG: Broadcasting transaction: {tx_hash}")
        
        success = False
        for endpoint in self.network_endpoints:
            for attempt in range(self.broadcast_retries):
                try:
                    # Prepare the broadcast data
                    broadcast_data = {
                        'transaction': transaction,
                        'timestamp': time.time(),
                        'node_id': 'luna_wallet_v1'
                    }
                    
                    # Send to network endpoint
                    response = requests.post(
                        f"{endpoint}/api/transaction/broadcast",
                        json=broadcast_data,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('success'):
                            print(f"DEBUG: Successfully broadcast to {endpoint}")
                            success = True
                            break
                        else:
                            print(f"DEBUG: Broadcast failed: {result.get('error', 'Unknown error')}")
                    else:
                        print(f"DEBUG: HTTP error {response.status_code} from {endpoint}")
                        
                except requests.exceptions.RequestException as e:
                    print(f"DEBUG: Network error broadcasting to {endpoint}: {e}")
                
                # Wait before retry
                if attempt < self.broadcast_retries - 1:
                    time.sleep(1)
        
        return success
    
    def get_transaction(self, tx_hash: str) -> Optional[Dict]:
        """Get transaction from mempool by hash"""
        if tx_hash in self.local_mempool:
            return self.local_mempool[tx_hash]['transaction']
        return None
    
    def get_pending_transactions(self, address: str = None) -> List[Dict]:
        """Get all pending transactions, optionally filtered by address"""
        transactions = []
        for tx_data in self.local_mempool.values():
            tx = tx_data['transaction']
            if address is None or tx.get('from') == address or tx.get('to') == address:
                transactions.append(tx)
        return transactions
    
    def remove_transaction(self, tx_hash: str):
        """Remove transaction from mempool (usually after confirmation)"""
        if tx_hash in self.local_mempool:
            del self.local_mempool[tx_hash]
            self.confirmed_transactions.add(tx_hash)
            print(f"DEBUG: Removed transaction from mempool: {tx_hash}")
    
    def is_transaction_pending(self, tx_hash: str) -> bool:
        """Check if transaction is pending in mempool"""
        return tx_hash in self.local_mempool
    
    def is_transaction_confirmed(self, tx_hash: str) -> bool:
        """Check if transaction has been confirmed"""
        return tx_hash in self.confirmed_transactions
    
    def get_mempool_size(self) -> int:
        """Get current mempool size"""
        return len(self.local_mempool)
    
    def clear_mempool(self):
        """Clear all transactions from mempool"""
        self.local_mempool.clear()
        print("DEBUG: Cleared mempool")
    
    def _broadcast_worker(self):
        """Background worker to broadcast pending transactions"""
        while self.is_running:
            try:
                # Process all pending broadcasts
                while not self.pending_broadcasts.empty():
                    transaction = self.pending_broadcasts.get()
                    tx_hash = transaction.get('hash')
                    
                    # Update broadcast info
                    if tx_hash in self.local_mempool:
                        self.local_mempool[tx_hash]['broadcast_attempts'] += 1
                        self.local_mempool[tx_hash]['last_broadcast'] = time.time()
                    
                    # Broadcast transaction
                    success = self.broadcast_transaction(transaction)
                    
                    if success:
                        print(f"DEBUG: Broadcast successful for {tx_hash}")
                    else:
                        print(f"DEBUG: Broadcast failed for {tx_hash}")
                        # Re-queue for retry if under limit
                        if (tx_hash in self.local_mempool and 
                            self.local_mempool[tx_hash]['broadcast_attempts'] < self.broadcast_retries):
                            self.pending_broadcasts.put(transaction)
                
                # Sleep before next iteration
                time.sleep(5)
                
            except Exception as e:
                print(f"DEBUG: Error in broadcast worker: {e}")
                time.sleep(10)
    
    def _cleanup_worker(self):
        """Background worker to clean up old transactions"""
        while self.is_running:
            try:
                current_time = time.time()
                expired_txs = []
                
                # Find transactions older than 1 hour
                for tx_hash, tx_data in self.local_mempool.items():
                    if current_time - tx_data['timestamp'] > 3600:  # 1 hour
                        expired_txs.append(tx_hash)
                
                # Remove expired transactions
                for tx_hash in expired_txs:
                    del self.local_mempool[tx_hash]
                    print(f"DEBUG: Removed expired transaction: {tx_hash}")
                
                # Clean up confirmed transactions set (keep only recent ones)
                if len(self.confirmed_transactions) > self.max_mempool_size * 2:
                    # Convert to list and keep only recent half
                    confirmed_list = list(self.confirmed_transactions)
                    self.confirmed_transactions = set(confirmed_list[-self.max_mempool_size:])
                
                # Sleep for 5 minutes
                time.sleep(300)
                
            except Exception as e:
                print(f"DEBUG: Error in cleanup worker: {e}")
                time.sleep(60)
    
    def _validate_transaction_basic(self, transaction: Dict) -> bool:
        """Basic transaction validation"""
        required_fields = ['type', 'from', 'to', 'amount', 'timestamp', 'hash']
        
        for field in required_fields:
            if field not in transaction:
                print(f"DEBUG: Missing required field: {field}")
                return False
        
        # Validate amount
        if transaction['amount'] <= 0:
            print("DEBUG: Invalid amount")
            return False
        
        # Validate timestamp (not too far in future)
        if transaction['timestamp'] > time.time() + 300:  # 5 minutes in future
            print("DEBUG: Transaction timestamp too far in future")
            return False
        
        return True
    
    def stop(self):
        """Stop the mempool manager"""
        self.is_running = False
        print("DEBUG: Mempool manager stopped")
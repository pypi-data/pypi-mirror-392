# lunalib/core/mempool.py - Updated version

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
                    # Try different possible endpoints
                    endpoints_to_try = [
                        f"{endpoint}/api/transaction/broadcast",
                        f"{endpoint}/api/transactions",
                        f"{endpoint}/mempool",
                        f"{endpoint}/api/mempool",
                        f"{endpoint}/api/v1/transaction/broadcast",
                        f"{endpoint}/api/v1/transactions"
                    ]
                    
                    for broadcast_endpoint in endpoints_to_try:
                        try:
                            print(f"DEBUG: Trying endpoint: {broadcast_endpoint}")
                            
                            # Prepare the broadcast data - try different formats
                            broadcast_data = {
                                'transaction': transaction,
                                'timestamp': time.time(),
                                'node_id': 'luna_wallet_v1'
                            }
                            
                            # Alternative: send transaction directly as JSON
                            headers = {
                                'Content-Type': 'application/json',
                                'User-Agent': 'LunaWallet/1.0'
                            }
                            
                            # Try sending the transaction
                            response = requests.post(
                                broadcast_endpoint,
                                json=broadcast_data,
                                headers=headers,
                                timeout=10
                            )
                            
                            print(f"DEBUG: Response status: {response.status_code}")
                            print(f"DEBUG: Response headers: {response.headers}")
                            
                            if response.status_code == 200:
                                result = response.json() if response.content else {}
                                print(f"DEBUG: Response data: {result}")
                                
                                if result.get('success') or response.status_code == 200:
                                    print(f"DEBUG: Successfully broadcast to {broadcast_endpoint}")
                                    success = True
                                    break
                                else:
                                    print(f"DEBUG: Broadcast failed: {result.get('error', 'Unknown error')}")
                            elif response.status_code == 201:
                                print(f"DEBUG: Successfully created at {broadcast_endpoint}")
                                success = True
                                break
                            else:
                                print(f"DEBUG: HTTP error {response.status_code} from {broadcast_endpoint}")
                                
                        except requests.exceptions.RequestException as e:
                            print(f"DEBUG: Network error broadcasting to {broadcast_endpoint}: {e}")
                            continue
                    
                    if success:
                        break
                        
                except Exception as e:
                    print(f"DEBUG: Exception during broadcast attempt {attempt + 1}: {e}")
                
                # Wait before retry
                if attempt < self.broadcast_retries - 1:
                    time.sleep(2)
        
        if not success:
            print(f"DEBUG: All broadcast attempts failed for transaction {tx_hash}")
        else:
            print(f"DEBUG: Broadcast successful for transaction {tx_hash}")
            
        return success
    
    def test_connection(self) -> bool:
        """Test connection to network endpoints"""
        for endpoint in self.network_endpoints:
            try:
                print(f"DEBUG: Testing connection to {endpoint}")
                response = requests.get(f"{endpoint}/", timeout=5)
                print(f"DEBUG: Connection test response: {response.status_code}")
                if response.status_code == 200:
                    print(f"DEBUG: Successfully connected to {endpoint}")
                    return True
            except Exception as e:
                print(f"DEBUG: Connection test failed for {endpoint}: {e}")
        
        print("DEBUG: All connection tests failed")
        return False
    
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
                # Test connection first
                if not self.test_connection():
                    print("DEBUG: No network connection, waiting...")
                    time.sleep(30)
                    continue
                
                # Process all pending broadcasts
                processed_count = 0
                while not self.pending_broadcasts.empty() and processed_count < 10:  # Limit per cycle
                    transaction = self.pending_broadcasts.get()
                    tx_hash = transaction.get('hash')
                    
                    # Update broadcast info
                    if tx_hash in self.local_mempool:
                        mempool_data = self.local_mempool[tx_hash]
                        if mempool_data['broadcast_attempts'] >= self.broadcast_retries:
                            print(f"DEBUG: Max broadcast attempts reached for {tx_hash}, removing")
                            del self.local_mempool[tx_hash]
                            continue
                        
                        mempool_data['broadcast_attempts'] += 1
                        mempool_data['last_broadcast'] = time.time()
                    
                    # Broadcast transaction
                    success = self.broadcast_transaction(transaction)
                    
                    if success:
                        print(f"DEBUG: Broadcast successful for {tx_hash}")
                        # Keep in mempool but don't re-broadcast
                    else:
                        print(f"DEBUG: Broadcast failed for {tx_hash}, attempt {mempool_data['broadcast_attempts']}")
                        # Re-queue for retry if under limit
                        if (tx_hash in self.local_mempool and 
                            self.local_mempool[tx_hash]['broadcast_attempts'] < self.broadcast_retries):
                            self.pending_broadcasts.put(transaction)
                    
                    processed_count += 1
                
                # Sleep before next iteration
                time.sleep(10)
                
            except Exception as e:
                print(f"DEBUG: Error in broadcast worker: {e}")
                time.sleep(30)
    
    def _cleanup_worker(self):
        """Background worker to clean up old transactions"""
        while self.is_running:
            try:
                current_time = time.time()
                expired_txs = []
                
                # Find transactions older than 1 hour or with too many failed attempts
                for tx_hash, tx_data in self.local_mempool.items():
                    if (current_time - tx_data['timestamp'] > 3600 or  # 1 hour
                        tx_data['broadcast_attempts'] >= self.broadcast_retries * 2):
                        expired_txs.append(tx_hash)
                
                # Remove expired transactions
                for tx_hash in expired_txs:
                    del self.local_mempool[tx_hash]
                    print(f"DEBUG: Removed expired/failed transaction: {tx_hash}")
                
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
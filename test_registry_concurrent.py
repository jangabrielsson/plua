#!/usr/bin/env python3
"""
Test just the registry save mechanism with concurrent writes
"""

import sys
import threading
import time
import random
import json
from pathlib import Path

# Simplified version of the registry save function for testing
def save_registry_test(registry_file, registry_data, thread_id):
    """Test version of _save_registry with robust locking"""
    import sys
    import tempfile
    import time
    import random
    
    max_retries = 5
    base_delay = 0.01  # 10ms base delay
    
    for attempt in range(max_retries):
        try:
            # Use unique temp file names to avoid conflicts
            timestamp = int(time.time() * 1000000)  # microseconds
            random_suffix = random.randint(1000, 9999)
            temp_file = registry_file.with_suffix(f'.json.tmp.{timestamp}.{random_suffix}')
            
            # Direct file locking on the registry file itself
            lock_acquired = False
            lock_fd = None
            
            try:
                # Try to acquire exclusive lock on registry file
                lock_fd = open(registry_file.with_suffix('.lockfile'), 'w')
                
                # Cross-platform file locking with timeout
                if sys.platform.startswith('win'):
                    # Windows: Use msvcrt for file locking
                    import msvcrt
                    for lock_attempt in range(10):  # 100ms timeout
                        try:
                            msvcrt.locking(lock_fd.fileno(), msvcrt.LK_NBLCK, 1)
                            lock_acquired = True
                            break
                        except OSError:
                            time.sleep(0.01)  # Wait 10ms
                else:
                    # Unix/Linux/macOS: Use fcntl with timeout
                    import fcntl
                    for lock_attempt in range(10):  # 100ms timeout
                        try:
                            fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                            lock_acquired = True
                            break
                        except (OSError, IOError):
                            time.sleep(0.01)  # Wait 10ms
                
                if not lock_acquired:
                    raise Exception(f"Could not acquire lock after timeout (attempt {attempt + 1})")
                
                print(f"Thread {thread_id}: Acquired lock on attempt {attempt + 1}")
                
                # Write to temporary file first
                with open(temp_file, 'w') as f:
                    json.dump(registry_data, f, indent=2)
                    f.write('\n')  # Ensure newline at end
                    f.flush()  # Ensure data is written
                    import os
                    os.fsync(f.fileno())  # Force to disk using os.fsync
                
                # Atomic rename (Windows requires removing target file first)
                if sys.platform.startswith('win') and registry_file.exists():
                    registry_file.unlink()  # Remove existing file on Windows
                temp_file.rename(registry_file)
                
                print(f"Thread {thread_id}: Successfully saved registry")
                # Success - exit retry loop
                return
                
            finally:
                # Always unlock and clean up
                if lock_acquired and lock_fd:
                    try:
                        if sys.platform.startswith('win'):
                            import msvcrt
                            msvcrt.locking(lock_fd.fileno(), msvcrt.LK_UNLCK, 1)
                        # fcntl locks are automatically released when file is closed
                    except Exception:
                        pass
                
                if lock_fd:
                    try:
                        lock_fd.close()
                    except Exception:
                        pass
                
                # Clean up temp file if it exists
                try:
                    if temp_file.exists():
                        temp_file.unlink()
                except Exception:
                    pass
                
                # Clean up lock file
                try:
                    lock_file = registry_file.with_suffix('.lockfile')
                    if lock_file.exists():
                        lock_file.unlink()
                except Exception:
                    pass
                    
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Thread {thread_id}: Failed to save registry after {max_retries} attempts: {e}")
                return
            else:
                # Exponential backoff with jitter
                delay = base_delay * (2 ** attempt) + random.uniform(0, 0.01)
                print(f"Thread {thread_id}: Attempt {attempt + 1} failed, retrying in {delay:.3f}s: {e}")
                time.sleep(delay)

def test_concurrent_registry_writes():
    """Test concurrent registry writes"""
    registry_file = Path.home() / ".plua" / "test_registry.json"
    
    # Clean up existing files
    try:
        registry_file.unlink()
    except FileNotFoundError:
        pass
    
    def worker(thread_id):
        """Worker function to write to registry"""
        registry_data = {
            "windows": {f"window_{thread_id}": {"qa_id": thread_id, "status": "open"}},
            "positions": {f"qa_{thread_id}": {"x": thread_id * 50, "y": thread_id * 50}}
        }
        
        save_registry_test(registry_file, registry_data, thread_id)
    
    # Create multiple threads
    threads = []
    thread_ids = [5555, 5556, 5557, 5558, 5559, 5560]
    
    print(f"Starting {len(thread_ids)} concurrent registry write threads...")
    
    for thread_id in thread_ids:
        thread = threading.Thread(target=worker, args=(thread_id,))
        threads.append(thread)
        thread.start()
        # Small delay to stagger starts
        time.sleep(0.005)  # 5ms
    
    # Wait for all threads
    for thread in threads:
        thread.join()
    
    print("\nAll threads completed")
    
    # Check final registry
    try:
        if registry_file.exists():
            with open(registry_file, 'r') as f:
                final_registry = json.load(f)
            print(f"\nFinal registry contains:")
            print(f"Windows: {len(final_registry.get('windows', {}))}")
            print(f"Positions: {len(final_registry.get('positions', {}))}")
            print(f"Registry file size: {registry_file.stat().st_size} bytes")
        else:
            print("No registry file created!")
    except Exception as e:
        print(f"Error reading final registry: {e}")
    
    # Clean up
    try:
        registry_file.unlink()
    except FileNotFoundError:
        pass

if __name__ == "__main__":
    print("Testing concurrent registry writes...")
    test_concurrent_registry_writes()
    print("Test completed")

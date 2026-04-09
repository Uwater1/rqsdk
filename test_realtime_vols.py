import rqdatac
import time
import sys

# Initialize the Ricequant SDK
rqdatac.init()

def monitor_volumes(order_book_ids):
    print(f"Monitoring Bid1/Ask1 for: {', '.join(order_book_ids)}")
    print("Format: [ID] Bid1: Price(Vol) | Ask1: Price(Vol)")
    
    try:
        while True:
            # Fetch snapshots for all IDs at once
            snapshots = rqdatac.current_snapshot(order_book_ids)
            
            # Ensure snapshots is a list if single ID was passed
            if not isinstance(snapshots, list):
                snapshots = [snapshots]
                
            results = []
            for snapshot in snapshots:
                if not snapshot:
                    continue
                
                # Get level 1 prices and volumes
                b1_p = snapshot.bids[0] if hasattr(snapshot, 'bids') and snapshot.bids else 0
                b1_v = snapshot.bid_vols[0] if hasattr(snapshot, 'bid_vols') and snapshot.bid_vols else 0
                a1_p = snapshot.asks[0] if hasattr(snapshot, 'asks') and snapshot.asks else 0
                a1_v = snapshot.ask_vols[0] if hasattr(snapshot, 'ask_vols') and snapshot.ask_vols else 0
                
                # Format single line result
                results.append(f"[{snapshot.order_book_id}] B1: {b1_p}({b1_v}) | A1: {a1_p}({a1_v})")
            
            # Print all in one line
            timestamp = time.strftime("%H:%M:%S")
            print(f"{timestamp} | " + " || ".join(results))
            
            # Flush stdout to ensure output appears immediately
            sys.stdout.flush()
            
            # Wait 15 seconds
            time.sleep(15)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    # Test IDs for IO, HO, and ETF options
    test_ids = ['IO2604C3950', 'HO2604C2500', '10010313']
    monitor_volumes(test_ids)

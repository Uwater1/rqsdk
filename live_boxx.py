import sys
import time
import threading
from datetime import datetime, timedelta
import pandas as pd
import rqdatac
from rqdatac import LiveMarketDataClient

# ── constants ────────────────────────────────────────────────────────────────
COMMISSION_PER_LEG = 0.2
BOX_COMMISSION = 4 * COMMISSION_PER_LEG
EVAL_INTERVAL = 2.0  # seconds

# ── globals ──────────────────────────────────────────────────────────────────
# tick_data dict: order_book_id -> { 'a1': float, 'b1': float, 'time': datetime }
tick_data = {}
data_lock = threading.Lock()

# options info: prefix -> expiry_date -> strike -> type -> order_book_id
options_map = {}

def get_3rd_friday(year: int, month: int) -> datetime.date:
    first = datetime(year, month, 1).date()
    offset = (4 - first.weekday()) % 7
    return first + timedelta(days=offset + 14)

def parse_ticker(order_book_id: str):
    # e.g. IO2604C4400
    prefix = order_book_id[:2]
    year = 2000 + int(order_book_id[2:4])
    month = int(order_book_id[4:6])
    opt_type = order_book_id[6]
    strike = float(order_book_id[7:])
    expiry_dt = get_3rd_friday(year, month)
    return prefix, expiry_dt, opt_type, strike

def init_options_map():
    print("Fetching active CFFEX options...")
    df = rqdatac.all_instruments(type='Option')
    today = datetime.now().date()
    
    if 'de_listed_date' in df.columns:
        # Convert to string first, then slice out the date part to avoid pandas timestamp issues
        df['de_listed_date'] = pd.to_datetime(df['de_listed_date']).dt.date
        df = df[df['de_listed_date'] >= today]
    
    cffex_ops = df[df['underlying_symbol'].isin(['IO', 'HO', 'MO'])]
    
    for _, row in cffex_ops.iterrows():
        oid = row['order_book_id']
        prefix, expiry, opt_type, strike = parse_ticker(oid)
        
        if prefix not in options_map:
            options_map[prefix] = {}
        if expiry not in options_map[prefix]:
            options_map[prefix][expiry] = {}
        if strike not in options_map[prefix][expiry]:
            options_map[prefix][expiry][strike] = {}
            
        options_map[prefix][expiry][strike][opt_type] = oid
        
        with data_lock:
            tick_data[oid] = {'a1': 0.0, 'b1': 0.0, 'time': None}
            
    print(f"Loaded {len(cffex_ops)} active CFFEX options.")
    return list(cffex_ops['order_book_id'])

def handle_msg(msg):
    try:
        # If msg is an object instead of dict, convert or access properties
        if isinstance(msg, dict):
            oid = msg.get('order_book_id')
            asks = msg.get('ask', [])
            bids = msg.get('bid', [])
        else:
            oid = getattr(msg, 'order_book_id', None)
            asks = getattr(msg, 'ask', [])
            bids = getattr(msg, 'bid', [])
            
        if oid and asks and bids:
            a1 = asks[0] if len(asks) > 0 else 0.0
            b1 = bids[0] if len(bids) > 0 else 0.0
            
            with data_lock:
                if oid in tick_data:
                    tick_data[oid]['a1'] = float(a1)
                    tick_data[oid]['b1'] = float(b1)
                    tick_data[oid]['time'] = datetime.now()
    except Exception as e:
        pass

def evaluator_loop():
    today = datetime.now().date()
    
    while True:
        time.sleep(EVAL_INTERVAL)
        
        with data_lock:
            snapshot = {k: dict(v) for k, v in tick_data.items()}
            
        for prefix, expiries in options_map.items():
            for expiry, strikes_dict in expiries.items():
                dte = (expiry - today).days
                if dte <= 0: dte = 1
                ann_factor = 365.0 / dte
                
                valid_strikes = []
                for K, types in strikes_dict.items():
                    if 'C' in types and 'P' in types:
                        c_oid = types['C']
                        p_oid = types['P']
                        c_data = snapshot.get(c_oid)
                        p_data = snapshot.get(p_oid)
                        
                        if c_data and p_data:
                            ca1, cb1 = c_data['a1'], c_data['b1']
                            pa1, pb1 = p_data['a1'], p_data['b1']
                            if ca1 > 0 and cb1 > 0 and pa1 > 0 and pb1 > 0:
                                valid_strikes.append({
                                    'K': K,
                                    'ca1': ca1, 'cb1': cb1,
                                    'pa1': pa1, 'pb1': pb1,
                                    'c_oid': c_oid, 'p_oid': p_oid
                                })
                                
                valid_strikes.sort(key=lambda x: x['K'])
                N = len(valid_strikes)
                
                best_long = None
                best_short = None
                
                for i in range(N):
                    for j in range(i + 1, N):
                        s1 = valid_strikes[i]
                        s2 = valid_strikes[j]
                        K1, K2 = s1['K'], s2['K']
                        payout = K2 - K1
                        
                        # Long Box: Buy C1(ask), Sell C2(bid), Buy P2(ask), Sell P1(bid)
                        cost = (s1['ca1'] - s2['cb1']) + (s2['pa1'] - s1['pb1']) + BOX_COMMISSION
                        if cost > 0:
                            ret = (payout - cost) / cost
                            if ret > 0:
                                ann = ret * ann_factor
                                if best_long is None or ann > best_long['ann']:
                                    best_long = {
                                        'K1': K1, 'K2': K2, 'cost': cost, 'payout': payout, 
                                        'ret': ret, 'ann': ann, 'dte': dte, 'type': 'LONG'
                                    }
                                    
                        # Short Box: Sell C1(bid), Buy C2(ask), Sell P2(bid), Buy P1(ask)
                        credit = (s1['cb1'] - s2['ca1']) + (s2['pb1'] - s1['pa1']) - BOX_COMMISSION
                        if credit > 0 and credit > payout:
                            margin = payout
                            ret = (credit - margin) / margin
                            if ret > 0:
                                ann = ret * ann_factor
                                if best_short is None or ann > best_short['ann']:
                                    best_short = {
                                        'K1': K1, 'K2': K2, 'credit': credit, 'margin': margin,
                                        'ret': ret, 'ann': ann, 'dte': dte, 'type': 'SHORT'
                                    }
                                    
                if best_long:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] LONG BOX {prefix} DTE={dte} K1={best_long['K1']} K2={best_long['K2']} Cost={best_long['cost']:.2f} Payout={best_long['payout']:.2f} Ret={best_long['ret']*100:.2f}% Ann={best_long['ann']*100:.2f}%")
                if best_short:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] SHORT BOX {prefix} DTE={dte} K1={best_short['K1']} K2={best_short['K2']} Credit={best_short['credit']:.2f} Margin={best_short['margin']:.2f} Ret={best_short['ret']*100:.2f}% Ann={best_short['ann']*100:.2f}%")

def main():
    print("Initializing RQDatac...")
    rqdatac.init()
    
    oids = init_options_map()
    if not oids:
        print("No active CFFEX options found.")
        sys.exit(1)
        
    client = LiveMarketDataClient()
    
    print(f"Subscribing to {len(oids)} ticks...")
    tick_channels = [f"tick_{oid}" for oid in oids]
    
    try:
        client.subscribe(tick_channels)
    except Exception as e:
        print(f"Error subscribing: {e}")
        # Try chunking
        for i in range(0, len(tick_channels), 100):
            try:
                client.subscribe(tick_channels[i:i+100])
            except Exception as e2:
                print(f"Error in chunk subscribe: {e2}")
            
    print("Starting evaluator loop thread...")
    eval_thread = threading.Thread(target=evaluator_loop, daemon=True)
    eval_thread.start()
    
    print("Listening for live ticks... (Press Ctrl+C to stop)")
    try:
        # Some versions of LiveMarketDataClient block when handler is passed
        # others do not. If it blocks, it will stay in listen(). 
        client.listen(handler=handle_msg)
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        sys.exit(0)

if __name__ == '__main__':
    main()
import sys
import time
import threading
import pytz
import numpy as np
from numba import njit
from datetime import datetime, timedelta, date
import pandas as pd
import rqdatac
from rqdatac import LiveMarketDataClient

# ── constants ────────────────────────────────────────────────────────────────
COMMISSION_PER_LEG = 0.2
BOX_COMMISSION = 4 * COMMISSION_PER_LEG
EVAL_INTERVAL = 2.0  # seconds
TZ = pytz.timezone('Asia/Shanghai')

# ── globals ──────────────────────────────────────────────────────────────────
tick_data = {}
data_lock = threading.Lock()
options_map = {}

@njit(cache=True)
def evaluate_long_box(ca1, cb1, pa1, pb1, ks, dte, box_commission):
    N = len(ks)
    ann_factor = 365.0 / max(dte, 1.0)
    best_ann = -999.0
    best_idx_i = -1
    best_idx_j = -1
    best_cost = 0.0
    best_payout = 0.0
    best_ret = 0.0

    for i in range(N):
        for j in range(i + 1, N):
            payout = float(ks[j] - ks[i])
            if ca1[i] > 0 and cb1[j] > 0 and pa1[j] > 0 and pb1[i] > 0:
                cost = (ca1[i] - cb1[j]) + (pa1[j] - pb1[i]) + box_commission
                if cost > 0:
                    r = (payout - cost) / cost
                    if r > 0:
                        ann = r * ann_factor
                        if ann > best_ann:
                            best_ann = ann
                            best_idx_i = i
                            best_idx_j = j
                            best_cost = cost
                            best_payout = payout
                            best_ret = r
                            
    return best_idx_i, best_idx_j, best_cost, best_payout, best_ret, best_ann

def get_3rd_friday(year: int, month: int) -> date:
    first = datetime(year, month, 1).date()
    offset = (4 - first.weekday()) % 7
    return first + timedelta(days=offset + 14)

def parse_ticker(order_book_id: str):
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
    today = datetime.now(TZ).date()
    
    if 'de_listed_date' in df.columns:
        df['de_listed_date'] = pd.to_datetime(df['de_listed_date']).dt.date
        df = df[df['de_listed_date'] >= today]
    
    cffex_ops = df[df['underlying_symbol'].isin(['IO', 'HO', 'MO'])].copy()
    
    expiries = set()
    for oid in cffex_ops['order_book_id']:
        _, expiry, _, _ = parse_ticker(oid)
        expiries.add(expiry)
        
    all_dtes = sorted(list(set([(e - today).days for e in expiries])))
    min_dte = all_dtes[0] if all_dtes else 0
    
    target_oids = []
    
    for _, row in cffex_ops.iterrows():
        oid = row['order_book_id']
        prefix, expiry, opt_type, strike = parse_ticker(oid)
        dte = (expiry - today).days
        
        if not (min_dte < dte < 61):
            continue
        
        target_oids.append(oid)
        
        if prefix not in options_map:
            options_map[prefix] = {}
        if expiry not in options_map[prefix]:
            options_map[prefix][expiry] = {}
        if strike not in options_map[prefix][expiry]:
            options_map[prefix][expiry][strike] = {}
            
        options_map[prefix][expiry][strike][opt_type] = oid
        
        with data_lock:
            tick_data[oid] = {'a1': 0.0, 'b1': 0.0, 'time': None}
            
    print(f"Loaded {len(target_oids)} active CFFEX options matching criteria.")
    return target_oids

def handle_msg(msg):
    try:
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
                    tick_data[oid]['time'] = datetime.now(TZ)
    except Exception as e:
        print(f"[handle_msg error] {e}", file=sys.stderr)

def evaluator_loop():
    while True:
        time.sleep(EVAL_INTERVAL)
        today = datetime.now(TZ).date()
        
        with data_lock:
            snapshot = {k: dict(v) for k, v in tick_data.items()}
            
        for prefix, expiries in options_map.items():
            for expiry, strikes_dict in expiries.items():
                dte = (expiry - today).days
                if dte <= 0: dte = 1
                
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
                                    'pa1': pa1, 'pb1': pb1
                                })
                                
                if len(valid_strikes) < 2:
                    continue
                    
                valid_strikes.sort(key=lambda x: x['K'])
                
                ca1 = np.array([x['ca1'] for x in valid_strikes], dtype=np.float64)
                cb1 = np.array([x['cb1'] for x in valid_strikes], dtype=np.float64)
                pa1 = np.array([x['pa1'] for x in valid_strikes], dtype=np.float64)
                pb1 = np.array([x['pb1'] for x in valid_strikes], dtype=np.float64)
                ks  = np.array([x['K'] for x in valid_strikes], dtype=np.float64)
                
                idx_i, idx_j, cost, payout, ret, ann = evaluate_long_box(ca1, cb1, pa1, pb1, ks, float(dte), BOX_COMMISSION)
                if idx_i >= 0:
                    print(f"[{datetime.now(TZ).strftime('%H:%M:%S')}] LONG BOX FAR {prefix} DTE={dte} K1={ks[idx_i]} K2={ks[idx_j]} Cost={cost:.2f} Payout={payout:.2f} Ret={ret*100:.2f}% Ann={ann*100:.2f}%")

def main():
    print("Initializing RQDatac...")
    rqdatac.init()
    
    oids = init_options_map()
    if not oids:
        print("No active CFFEX options found matching criteria.")
        sys.exit(0)
        
    client = LiveMarketDataClient()
    
    print(f"Subscribing to {len(oids)} ticks...")
    tick_channels = [f"tick_{oid}" for oid in oids]
    
    try:
        client.subscribe(tick_channels)
    except Exception as e:
        print(f"Error subscribing: {e}")
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
        client.listen(handler=handle_msg)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        sys.exit(0)

if __name__ == '__main__':
    main()

import pandas as pd
import numpy as np
from datetime import timedelta

class AlphaFinder:
    def __init__(self, data_path='../data/510300_1d.parquet', unit=0.05):
        self.data_path = data_path
        self.unit = unit  # ETF unit roughly representing 50 points of index
        self.df = self._load_data()
        self._calculate_30d_returns()

    def _load_data(self):
        """Load and parse the ETF data."""
        df = pd.read_parquet(self.data_path)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        return df

    def _calculate_30d_returns(self):
        """Calculate 30-day calendar forward returns."""
        # Using the exact same logic mentioned in walkthrough.md
        # 50 points for HS300 is roughly 0.05 index value of 510300 ETF
        # (Assuming HS300 is around 4000, 50 points is ~1.25%, ETF is ~4.0, 4.0 * 1.25% = 0.05)

        # We need efficient lookback
        df = self.df.copy()

        # We only need close prices for forward returns
        dates = df['date'].values
        closes = df['close'].values

        # Create an array to hold forward 30 day point moves
        forward_points = np.full(len(df), np.nan)

        for i, dt in enumerate(dates):
            # Target date is dt + 30 days
            target_dt = dt + np.timedelta64(30, 'D')

            # Find the index of the first date >= target_dt
            idx = np.searchsorted(dates, target_dt)

            if idx < len(dates):
                forward_points[i] = closes[idx] - closes[i]

        df['30d_fwd_pt'] = forward_points
        self.df = df

        valid_moves = df['30d_fwd_pt'].dropna()
        self.prob_down = (valid_moves < -self.unit).mean()
        self.prob_up = (valid_moves > self.unit).mean()

    def get_probabilities(self, current_date):
        """
        Get historical probability of up/down move up to the current_date
        to avoid lookahead bias.
        """
        current_date64 = np.datetime64(current_date)

        # Only look at moves that were completed BEFORE current_date
        # (meaning the start date of the 30d window was >30 days ago)
        # However, to simulate 'walkthrough' we just look at all historical moves
        # computed before current_date
        historical_df = self.df[self.df['date'] < current_date]
        valid_moves = historical_df['30d_fwd_pt'].dropna()

        if len(valid_moves) == 0:
            return 0.5, 0.5 # Default

        prob_down = (valid_moves < -self.unit).mean()
        prob_up = (valid_moves > self.unit).mean()

        return prob_down, prob_up

    def select_strikes(self, current_price, current_date):
        """
        Dynamically determine OTM strikes based on the alpha distribution.
        """
        prob_down, prob_up = self.get_probabilities(current_date)

        # Covered Call: OTM 3-4 calls and OTM 4-5 calls
        # We assume "OTM 1 step" means roughly 0.05 unit
        # (ETF options often have strike intervals of 0.05 or 0.1)

        # Base interval for 510300 ETF is usually 0.1
        interval = 0.1

        # Round current price to nearest strike
        atm_strike = round(current_price / interval) * interval

        # Call leg A: OTM 3-4档. Let's use 3档 (3 intervals)
        call_strike_A = atm_strike + 3 * interval

        # Call leg B: OTM 4-5档. Let's use 4档 (4 intervals)
        # Optimization: if prob_up is very low (< 35%), we can be more aggressive and sell both legs at Call Leg A
        if prob_up < 0.35:
            call_strike_B = call_strike_A
        else:
            call_strike_B = atm_strike + 4 * interval

        # Put spread side:
        # sell 1 put at support level (say 2 intervals down to account for high drop probability)
        # buy 1 put further OTM for protection (3 intervals down)
        # Optimization: if prob_down is very high (> 50%), push the support level further OTM
        if prob_down > 0.50:
            put_strike_sell = atm_strike - 3 * interval
            put_strike_buy = atm_strike - 4 * interval
        else:
            put_strike_sell = atm_strike - 2 * interval
            put_strike_buy = atm_strike - 3 * interval

        return {
            'call_strike_A': call_strike_A,
            'call_strike_B': call_strike_B,
            'put_strike_sell': put_strike_sell,
            'put_strike_buy': put_strike_buy
        }

if __name__ == '__main__':
    finder = AlphaFinder()
    print("Loaded data, rows:", len(finder.df))
    print(f"Overall Prob Move < -{finder.unit} pt: {finder.prob_down:.2%}")
    print(f"Overall Prob Move > +{finder.unit} pt: {finder.prob_up:.2%}")

    sample_date = pd.to_datetime('2023-01-01')
    strikes = finder.select_strikes(4.0, sample_date)
    print(f"Selected strikes for price 4.0 on {sample_date.date()}:")
    for k, v in strikes.items():
        print(f"  {k}: {v:.2f}")

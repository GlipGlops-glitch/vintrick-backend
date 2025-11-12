#    python tools/bit/backtrader_ORB.py


import pandas as pd
import numpy as np
import datetime

CONFIG = {
    "csv_path": r'C:\Users\cah01\Code\Vintrick\vintrick-backend\tools\bit\btcusd_1-min_data.csv',
    "start_date": "2021-01-01",
    "end_date": "2025-10-31",
    "init_cash": 2000,
    "min_cash": 10,
    "monthly_profit_hold_perc": 0.00,
    "risk_perc": 0.10,
    "first_candle_minutes": 30,
    "atr_period": 14,
    "sma_period": 35,
    "vol_period": 10,
    "tp_decrease_per_day": 0.02,
    "tp_min_perc": -0.01,
    "min_unit": 1e-8,
    "range_tp_percs": [
        {"min": None, "max": 115000, "perc": 0.10},
        {"min": 115000, "max": 120000, "perc": 0.08},
        {"min": 120000, "max": 122000, "perc": 0.035},
        {"min": 122000, "max": 123000, "perc": 0.03},
        {"min": 123000, "max": None, "perc": 0.025},
    ],
    "session_start_hour": 6,
    "session_start_minute": 30,

    # FILTER TOGGLES
    "use_atr_filter": False,
    "use_sma_filter": False,
    "use_vol_filter": False,

    # MAX PRICE FILTER
    "max_entry_price": 121000,

    # FORCE EXIT TOGGLE
    "use_force_exit": True,

    # FORCE EXIT AFTER X DAYS
    "force_exit_after_days": 3,   # None disables; set to integer to force exit after X days
}

def load_data(config):
    df = pd.read_csv(config["csv_path"])
    df['datetime'] = pd.to_datetime(df['Timestamp'], unit='s')
    df.set_index('datetime', inplace=True)
    df.drop(columns=['Timestamp'], inplace=True)
    df = df[(df.index >= pd.Timestamp(config["start_date"])) & 
            (df.index <= pd.Timestamp(config["end_date"]))].copy()
    shift_amt = 1440
    for col in ['Open', 'Close', 'High', 'Low']:
        df[f'prev_{col.lower()}'] = df[col].shift(shift_amt)
    df['date'] = df.index.date
    df['month'] = df.index.month
    df['year'] = df.index.year
    return df

def calculate_indicators(df, config):
    df['H-L'] = df['High'] - df['Low']
    df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
    df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    df['ATR'] = df['TR'].rolling(window=config['atr_period']).mean()
    df['SMA'] = df['Close'].rolling(window=config['sma_period']).mean()
    df['vol_avg'] = df['Volume'].rolling(window=config['vol_period']).mean()
    return df

def detect_fvg(df, idx):
    if idx < 2: return None
    c1 = df.iloc[idx-2]
    c2 = df.iloc[idx-1]
    if c2['Low'] > c1['High']:
        return {'type': 'bullish', 'high': c1['High'], 'low': c2['Low'], 'idx': idx-1}
    return None

def get_tp_perc_for_price(price, config):
    for r in config["range_tp_percs"]:
        minv = r["min"]
        maxv = r["max"]
        if (minv is None or price >= minv) and (maxv is None or price < maxv):
            return r["perc"]
    return config.get("take_profit_perc", 0.03)

def execute_trade(row, first_high, config, cash, held_cash, initial_tp_perc=None):
    price = row['Close']
    atr = row['ATR']
    sma = row['SMA']
    vol_avg = row['vol_avg']
    vol = row['Volume']

    # MAX PRICE FILTER
    max_entry_price = config.get("max_entry_price", None)
    if max_entry_price is not None and price > max_entry_price:
        return None

    # ATR FILTER
    if config.get("use_atr_filter", True):
        if pd.isna(atr) or atr <= 0:
            return None
    # SMA FILTER
    if config.get("use_sma_filter", True):
        if pd.isna(sma) or price < sma:
            return None
    # VOLUME FILTER
    if config.get("use_vol_filter", True):
        if pd.isna(vol_avg) or vol < vol_avg:
            return None

    risk_amt = (cash - held_cash) * config['risk_perc']
    position_size = risk_amt / (atr if atr > 0 else 1)
    max_affordable_size = (cash - held_cash) / price
    position_size = min(position_size, max_affordable_size)
    if position_size < config['min_unit']:
        return None
    if initial_tp_perc is None:
        initial_tp_perc = get_tp_perc_for_price(price, config)
    take_profit = price * (1 + initial_tp_perc)
    actual_dollar_risk = position_size * atr
    return {
        'type': 'long',
        'entry_price': price,
        'take_profit': take_profit,
        'size': position_size,
        'atr': atr,
        'actual_dollar_risk': actual_dollar_risk,
        'take_profit_perc_used': initial_tp_perc,
        'entry_day': row['date'],
        'entry_time': row.name,  # datetime index
    }

def run_backtest(df, config):
    cash = config['init_cash']
    held_cash = 0.0
    monthly_profit = 0.0
    current_month = None
    trades = []
    open_trade = None
    last_trade_day = None
    first_candle_end = None
    trade_made_today = False
    tp_perc_current = None
    tp_min_perc = config['tp_min_perc']
    force_exit_days = config.get('force_exit_after_days', None)

    for i in range(len(df)):
        row = df.iloc[i]
        dt = row.name
        day = row['date']
        month = row['month']
        year = row['year']

        if current_month is None:
            current_month = (year, month)
        elif (year, month) != current_month:
            if monthly_profit > 0:
                profit_to_hold = monthly_profit * config['monthly_profit_hold_perc']
                held_cash += profit_to_hold
                print(f"--- End of month {current_month}: Holding {config['monthly_profit_hold_perc']*100:.0f}% of profit ({profit_to_hold:.2f}) as cash. Held cash: {held_cash:.2f}")
            monthly_profit = 0.0
            current_month = (year, month)

        # Daily session start at 6:30am UTC
        if last_trade_day != day:
            session_start = dt.replace(hour=config["session_start_hour"], minute=config["session_start_minute"], second=0, microsecond=0)
            first_candle_end = session_start + datetime.timedelta(minutes=config['first_candle_minutes'])
            day_slice = df.loc[(df.index >= session_start) & (df.index < first_candle_end)]
            first_high = day_slice['High'].max() if not day_slice.empty else row['High']
            first_low = day_slice['Low'].min() if not day_slice.empty else row['Low']
            trade_made_today = False
            last_trade_day = day

        # Check for new trade (only if no open trade)
        if dt >= first_candle_end and not trade_made_today and (cash - held_cash) > config['min_cash'] and open_trade is None:
            tp_perc_current = None
            tp_perc_current = get_tp_perc_for_price(row['Close'], config)
            if row['Close'] > first_high:
                trade = execute_trade(row, first_high, config, cash, held_cash, initial_tp_perc=tp_perc_current)
                if trade:
                    trade_record = {
                        'entry_time': dt,
                        'type': trade['type'],
                        'entry_price': trade['entry_price'],
                        'take_profit': trade['take_profit'],
                        'size': trade['size'],
                        'atr': trade['atr'],
                        'actual_dollar_risk': trade['actual_dollar_risk'],
                        'take_profit_perc_used': trade['take_profit_perc_used'],
                        'reason': 'first_candle_breakout',
                        'exit_time': None,
                        'exit_price': None,
                        'pnl': None,
                        'entry_day': day,
                    }
                    open_trade = trade_record
                    trade_made_today = True
                    trades.append(trade_record)
                    print(f"{dt} First Candle Long breakout: {trade['entry_price']:.2f}, TP: {trade['take_profit']:.2f}, TP% Used: {trade['take_profit_perc_used']:.2%}, Size: {trade['size']:.8f}, Dollar Risk: {trade['actual_dollar_risk']:.2f}")

            fvg = detect_fvg(df, i)
            if fvg and not trade_made_today and (cash - held_cash) > config['min_cash'] and open_trade is None:
                if fvg['type'] == 'bullish' and row['Close'] <= fvg['high']:
                    tp_perc_current = get_tp_perc_for_price(row['Close'], config)
                    trade = execute_trade(row, first_high, config, cash, held_cash, initial_tp_perc=tp_perc_current)
                    if trade:
                        trade_record = {
                            'entry_time': dt,
                            'type': trade['type'],
                            'entry_price': trade['entry_price'],
                            'take_profit': trade['take_profit'],
                            'size': trade['size'],
                            'atr': trade['atr'],
                            'actual_dollar_risk': trade['actual_dollar_risk'],
                            'take_profit_perc_used': trade['take_profit_perc_used'],
                            'reason': 'fvg_fill',
                            'exit_time': None,
                            'exit_price': None,
                            'pnl': None,
                            'entry_day': day,
                        }
                        open_trade = trade_record
                        trade_made_today = True
                        trades.append(trade_record)
                        print(f"{dt} FVG Bullish fill entry at {trade['entry_price']:.2f}, TP: {trade['take_profit']:.2f}, TP% Used: {trade['take_profit_perc_used']:.2%}, Size: {trade['size']:.8f}, Dollar Risk: {trade['actual_dollar_risk']:.2f}")

        # Dynamic TP decrease logic - only if trade is open
        if open_trade:
            current_trade_day = row['date']
            if current_trade_day != open_trade['entry_day']:
                old_tp_perc = tp_perc_current
                tp_perc_current = max(tp_perc_current - config['tp_decrease_per_day'], config['tp_min_perc'])
                open_trade['take_profit_perc_used'] = tp_perc_current
                open_trade['take_profit'] = open_trade['entry_price'] * (1 + tp_perc_current)
                open_trade['entry_day'] = current_trade_day
                print(f"{dt} TP percent decreased to {tp_perc_current:.4f} ({tp_perc_current*100:.2f}%). New TP: {open_trade['take_profit']:.2f}")

                # --------- FORCE EXIT TOGGLE LOGIC ----------
                if config.get("use_force_exit", True) and tp_perc_current <= config['tp_min_perc']:
                    exit_price = row['Close']
                    pnl = (exit_price - open_trade['entry_price']) * open_trade['size']
                    cash += pnl
                    monthly_profit += pnl
                    print(f"{dt} Forced exit at {exit_price:.2f} due to TP% ({tp_perc_current*100:.2f}%) below minimum. Money made: {pnl:.2f}. Cash: {cash:.2f}")
                    open_trade['exit_time'] = dt
                    open_trade['exit_price'] = exit_price
                    open_trade['pnl'] = pnl
                    trades[-1].update({
                        'exit_time': dt,
                        'exit_price': exit_price,
                        'pnl': pnl
                    })
                    open_trade = None
                # --------------------------------------------

            # --------- FORCE EXIT AFTER X DAYS LOGIC ----------
            if force_exit_days is not None and open_trade is not None and open_trade.get('entry_time') is not None:
                days_held = (dt.date() - open_trade['entry_time'].date()).days
                if days_held >= force_exit_days:
                    exit_price = row['Close']
                    pnl = (exit_price - open_trade['entry_price']) * open_trade['size']
                    cash += pnl
                    monthly_profit += pnl
                    print(f"{dt} Forced exit after {days_held} days at {exit_price:.2f}. Money made: {pnl:.2f}. Cash: {cash:.2f}")
                    open_trade['exit_time'] = dt
                    open_trade['exit_price'] = exit_price
                    open_trade['pnl'] = pnl
                    trades[-1].update({
                        'exit_time': dt,
                        'exit_price': exit_price,
                        'pnl': pnl,
                        'reason': f'forced_exit_after_{days_held}_days'
                    })
                    open_trade = None
            # --------------------------------------------

        # Trade exit logic: sell immediately on take profit hit
        if open_trade:
            price = row['Close']
            if price >= open_trade['take_profit']:
                exit_price = price
                pnl = (exit_price - open_trade['entry_price']) * open_trade['size']
                cash += pnl
                monthly_profit += pnl
                print(f"{dt} Trade closed at {exit_price:.2f}. Money made: {pnl:.2f}. Cash: {cash:.2f}")
                open_trade['exit_time'] = dt
                open_trade['exit_price'] = exit_price
                open_trade['pnl'] = pnl
                trades[-1].update({
                    'exit_time': dt,
                    'exit_price': exit_price,
                    'pnl': pnl
                })
                open_trade = None

    final_price = df['Close'].iloc[-1]
    final_time = df.index[-1]
    for trade in trades:
        if trade['exit_price'] is None:
            trade['exit_time'] = final_time
            trade['exit_price'] = final_price
            trade['pnl'] = (final_price - trade['entry_price']) * trade['size']

    print(f"Final Cash: {cash:.2f}, Held Cash: {held_cash:.2f}")
    return trades

def main():
    df = load_data(CONFIG)
    df = calculate_indicators(df, CONFIG)
    trades = run_backtest(df, CONFIG)
    results = pd.DataFrame(trades)
    if not results.empty:
        print(results[['entry_time', 'exit_time', 'type', 'entry_price', 'exit_price', 'take_profit', 'take_profit_perc_used', 'size', 'atr', 'actual_dollar_risk', 'pnl', 'reason']])
        results.to_csv("trade_results_percent_tp_actual_risk_tp_decreases_forced_exit.csv", index=False)
    else:
        print("No trades executed.")

if __name__ == "__main__":
    main()
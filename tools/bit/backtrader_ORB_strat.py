#    python tools/bit/backtrader_ORB_strat.py
import pandas as pd
import numpy as np
import itertools
import datetime

# ---- STEP 1: Load your CSV ----
CSV_PATH = r"C:\Users\cah01\Code\Vintrick\vintrick-backend\tools\bit\btcusd_1-min_data.csv"
df = pd.read_csv(CSV_PATH)
df['datetime'] = pd.to_datetime(df['Timestamp'], unit='s')
df.set_index('datetime', inplace=True)

# ---- Filter to last N years ----
N_YEARS = 1  # Change this value to select a different number of years
cutoff = df.index.max() - pd.DateOffset(years=N_YEARS)
df = df[df.index >= cutoff]

# ---- STEP 2: Define strategy parameter search space ----
search_space = {
    "risk_perc": [0.05, 0.1, 0.2],
    "tp_perc": [0.03, 0.05, 0.07],
    "atr_period": [7, 14, 21],
    "sma_period": [21, 35, 50],
    "vol_period": [10, 20],
    "entry_type": ["ORB", "FVG"],  # could add "SMA_cross", "RSI", etc.
    "exit_type": ["tp", "trailing", "time"],
}

# ---- STEP 3: Generate all parameter combinations ----
param_names = list(search_space.keys())
param_values = list(search_space.values())
param_combos = list(itertools.product(*param_values))

# ---- STEP 4: Strategy logic ----
def run_strategy(df, params):
    # Calculate indicators
    df = df.copy()
    df['ATR'] = (df['High'] - df['Low']).rolling(window=params['atr_period']).mean()
    df['SMA'] = df['Close'].rolling(window=params['sma_period']).mean()
    df['vol_avg'] = df['Volume'].rolling(window=params['vol_period']).mean()
    trades = []
    cash = 1500
    min_cash = 50

    open_trade = None
    for i in range(len(df)):
        row = df.iloc[i]
        dt = row.name

        # ---- ENTRY RULES ----
        entry_signal = False
        if params['entry_type'] == "ORB":
            # Simple ORB: Close breaks previous high, after first 30 min (can optimize)
            if i > 30 and row['Close'] > df['High'].iloc[i-30:i].max():
                entry_signal = True
        elif params['entry_type'] == "FVG":
            # FVG: previous low > previous high (simple)
            if i > 2 and df['Low'].iloc[i-1] > df['High'].iloc[i-2]:
                entry_signal = True

        # ---- FILTERS ----
        # Only trade if volume above average and price above SMA
        if not entry_signal or row['Volume'] < row['vol_avg'] or row['Close'] < row['SMA']:
            continue
        if cash < min_cash:
            continue

        # ---- ENTRY ----
        # Position Sizing
        risk_amt = cash * params['risk_perc']
        position_size = risk_amt / (row['ATR'] if row['ATR'] > 0 else 1)
        max_affordable_size = cash / row['Close']
        position_size = min(position_size, max_affordable_size)
        position_cost = position_size * row['Close']
        if position_cost < min_cash:
            continue

        # ---- EXIT rules ----
        tp_price = row['Close'] * (1 + params['tp_perc'])
        trailing_buffer = 0.03  # 3% trailing stop
        max_days = 10
        entry_day = dt.date()
        days_open = 0

        for j in range(i+1, len(df)):
            exit_row = df.iloc[j]
            days_open = (exit_row.name.date() - entry_day).days
            # Take Profit
            if params['exit_type'] == "tp" and exit_row['Close'] >= tp_price:
                pnl = (exit_row['Close'] - row['Close']) * position_size
                cash += pnl
                trades.append({
                    "entry_time": dt, "exit_time": exit_row.name,
                    "entry_price": row['Close'], "exit_price": exit_row['Close'],
                    "type": "long", "size": position_size, "pnl": pnl,
                    "strategy_params": params
                })
                break
            # Trailing Stop
            elif params['exit_type'] == "trailing":
                trailing_tp = max(tp_price, exit_row['Close'] * (1 - trailing_buffer))
                if exit_row['Close'] < trailing_tp:
                    pnl = (exit_row['Close'] - row['Close']) * position_size
                    cash += pnl
                    trades.append({
                        "entry_time": dt, "exit_time": exit_row.name,
                        "entry_price": row['Close'], "exit_price": exit_row['Close'],
                        "type": "long", "size": position_size, "pnl": pnl,
                        "strategy_params": params
                    })
                    break
            # Time-based exit
            elif params['exit_type'] == "time" and days_open >= max_days:
                pnl = (exit_row['Close'] - row['Close']) * position_size
                cash += pnl
                trades.append({
                    "entry_time": dt, "exit_time": exit_row.name,
                    "entry_price": row['Close'], "exit_price": exit_row['Close'],
                    "type": "long", "size": position_size, "pnl": pnl,
                    "strategy_params": params
                })
                break
            # Stop after max days anyway
            if days_open > max_days:
                break

    # ---- Metrics ----
    total_pnl = sum([t['pnl'] for t in trades])
    win_rate = np.mean([t['pnl'] > 0 for t in trades]) if trades else 0
    max_drawdown = min([t['pnl'] for t in trades]) if trades else 0
    return {"profit": total_pnl, "win_rate": win_rate, "max_drawdown": max_drawdown, "trades": trades}

# ---- STEP 5: Run and score all strategies ----
results = []
for combo in param_combos:
    params = dict(zip(param_names, combo))
    metrics = run_strategy(df, params)
    results.append((params, metrics))

# ---- STEP 6: Sort and select best strategies ----
results_sorted = sorted(results, key=lambda x: x[1]['profit'], reverse=True)
print("Top 5 strategies by profit:")
for i in range(5):
    params, metrics = results_sorted[i]
    print(f"\nStrategy {i+1}: {params}")
    print(f"Profit: {metrics['profit']:.2f}, Win Rate: {metrics['win_rate']:.2%}, Max Drawdown: {metrics['max_drawdown']:.2f}")
    print(f"Trades: {len(metrics['trades'])}")

# ---- STEP 7: Save best trades to CSV ----
best_params, best_metrics = results_sorted[0]
trades_df = pd.DataFrame(best_metrics['trades'])
trades_df.to_csv("best_strategy_trades.csv", index=False)

print("\nBest strategy trades saved to 'best_strategy_trades.csv'")
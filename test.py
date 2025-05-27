import pandas as pd 
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import mplcursors  # NEW

# Load and preprocess
df = pd.read_csv('./Data/LPPL_AI_SNP.csv')
df['Date'] = pd.to_datetime(df['Date'])
df['LogPrice'] = np.log(df['Close'])

# 색상 맵핑
color_map = {'green': '#b0f4b4', 'orange': '#f7e4a0', 'red': '#f4a09c'}
df_plot = df[['Date', 'LogPrice', 'color', 'Close']].copy()  # 종가 포함

def plot_interactive_graph(ax, df, title):
    df_sorted = df.sort_values('Date').reset_index(drop=True)
    x = df_sorted['Date'].values
    y = df_sorted['LogPrice'].values

    # 배경 색상 (S&P 500 아래만)
    for label, color in color_map.items():
        mask = (df_sorted['color'] == label).values
        ax.fill_between(x, y.min(), y, where=mask, color=color, alpha=0.5, interpolate=True, zorder=0)

    # S&P 500 선
    line, = ax.plot(x, y, color='black', linewidth=1.5, label='S&P 500', zorder=1)
    ax.set_title(title)
    ax.set_ylabel('Log price')
    ax.legend(handles=[
        Patch(color=color_map['red'], label='Crash-alert'),
        Patch(color=color_map['orange'], label='Caution'),
        Patch(color=color_map['green'], label='Stable'),
        Patch(color='black', label='S&P 500')
    ])
    ax.grid(False)

    # 인터랙티브 커서 추가
    cursor = mplcursors.cursor(line, hover=True)

    @cursor.connect("add")
    def on_add(sel):
        idx = sel.index
        date_str = df_sorted['Date'].iloc[idx].strftime('%Y-%m-%d')
        close = df_sorted['Close'].iloc[idx]
        sel.annotation.set(text=f"{date_str}\nClose: {close:.2f}", fontsize=10)

# 플롯
fig, ax = plt.subplots(1, 1, figsize=(12, 8), sharex=True)
plot_interactive_graph(ax, df_plot, '(b) DTCAI')
ax.set_xlabel('Date')
plt.tight_layout()
plt.show()

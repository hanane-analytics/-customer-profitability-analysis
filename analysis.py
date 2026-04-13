import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ── LOAD ─────────────────────────────────────────────────
df = pd.read_csv('pareto_profitability.csv')

# ── BASIC INFO ────────────────────────────────────────────
print(df.head())
losing = df[df['total_profit'] < 0]
print(f"\nLosing customers: {len(losing)} ({len(losing)/len(df)*100:.1f}%)")

# ── PARETO ANALYSIS ───────────────────────────────────────
df_sorted = df.sort_values('total_profit', ascending=False).reset_index(drop=True)

total_positive_profit = df_sorted[df_sorted['total_profit'] > 0]['total_profit'].sum()
df_sorted['cumulative_profit'] = df_sorted['total_profit'].cumsum()
df_sorted['cumulative_profit_pct'] = df_sorted['cumulative_profit'] / total_positive_profit * 100
df_sorted['customer_pct'] = (df_sorted.index + 1) / len(df_sorted) * 100

# ── SEGMENTS ─────────────────────────────────────────────
pareto = df_sorted[df_sorted['cumulative_profit_pct'] <= 80].tail(1)
print(f"\nTop 80% of profit comes from: {pareto['customer_pct'].values[0]:.1f}% of customers")

df_sorted['segment'] = 'Losing'
df_sorted.loc[df_sorted['cumulative_profit_pct'] <= 80, 'segment'] = 'Top'
df_sorted.loc[(df_sorted['cumulative_profit_pct'] > 80) &
              (df_sorted['total_profit'] > 0), 'segment'] = 'Average'

print("\nSegment counts:")
print(df_sorted['segment'].value_counts())
print("\nProfit by segment:")
print(df_sorted.groupby('segment')['total_profit'].sum())

# ── TOP CUSTOMERS PROFILE ─────────────────────────────────
top = df_sorted[df_sorted['segment'] == 'Top']
print("\n--- Top Customers ---")
print("Acquisition Channel:")
print(top['acquisition_channel'].value_counts(normalize=True)*100)
print("\nCustomer Type:")
print(top['customer_type'].value_counts(normalize=True)*100)
print(f"\nAvg Orders: {top['total_orders'].mean():.1f}")
print(f"Avg Order Value: {top['avg_order_value'].mean():.1f}")

# ── LOSING CUSTOMERS PROFILE ──────────────────────────────
losing_seg = df_sorted[df_sorted['segment'] == 'Losing']
print("\n--- Losing Customers ---")
print("Acquisition Channel:")
print(losing_seg['acquisition_channel'].value_counts(normalize=True)*100)
print("\nCustomer Type:")
print(losing_seg['customer_type'].value_counts(normalize=True)*100)
print(f"\nAvg Orders: {losing_seg['total_orders'].mean():.1f}")
print(f"Return Rate: {losing_seg['return_rate'].mean():.2f}")

# ── VISUALIZATION ─────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Customer Profitability Analysis — Pareto Principle',
             fontsize=16, fontweight='bold', y=1.02)

segments = ['Top', 'Average', 'Losing']
colors = ['#639922', '#378ADD', '#E24B4A']

# Graph 1: Profit by Segment
profits = [1819516, 1110018, -653892]
axes[0,0].bar(segments, profits, color=colors, width=0.5)
axes[0,0].set_title('Total Profit by Customer Segment', fontweight='bold')
axes[0,0].set_ylabel('Total Profit')
axes[0,0].axhline(y=0, color='black', linewidth=0.8)
for i, v in enumerate(profits):
    axes[0,0].text(i, v + 20000 if v > 0 else v - 60000,
                   f'{v:,}', ha='center', fontweight='bold', fontsize=9)

# Graph 2: Pareto Curve
axes[0,1].plot(df_sorted['customer_pct'],
               df_sorted['cumulative_profit_pct'],
               color='#378ADD', linewidth=2)
axes[0,1].axvline(x=7.7, color='#E24B4A', linestyle='--', label='Top segment')
axes[0,1].axhline(y=80, color='#639922', linestyle='--', label='80% of profit')
axes[0,1].set_title('Pareto Curve — Profit Concentration', fontweight='bold')
axes[0,1].set_xlabel('% of Customers')
axes[0,1].set_ylabel('% of Cumulative Profit')
axes[0,1].legend()
axes[0,1].set_xlim(0, 100)
axes[0,1].set_ylim(0, 110)

# Graph 3: Avg Orders by Segment
seg_orders = [16.0, 5.5, 2.2]
axes[1,0].bar(segments, seg_orders, color=colors, width=0.5)
axes[1,0].set_title('Average Orders by Segment', fontweight='bold')
axes[1,0].set_ylabel('Avg Number of Orders')
for i, v in enumerate(seg_orders):
    axes[1,0].text(i, v + 0.2, f'{v}', ha='center', fontweight='bold')

# Graph 4: Return Rate by Segment
return_rates = [5, 12, 24]
axes[1,1].bar(segments, return_rates, color=colors, width=0.5)
axes[1,1].set_title('Return Rate by Segment', fontweight='bold')
axes[1,1].set_ylabel('Return Rate %')
for i, v in enumerate(return_rates):
    axes[1,1].text(i, v + 0.3, f'{v}%', ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('customer_profitability_analysis.png', dpi=150, bbox_inches='tight')
plt.show()

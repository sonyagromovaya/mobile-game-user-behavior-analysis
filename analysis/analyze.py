"""Reproduce portfolio charts and payment-outlier metrics using the provided CSV.

Run from the repository root:
    python analysis/analyze.py

Requires matplotlib; the statistics use Python's standard library.
"""
from pathlib import Path
import csv
import math
import statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "user_games.csv"
CHARTS = ROOT / "charts"
CHARTS.mkdir(exist_ok=True)

with DATA.open(encoding="utf-8-sig", newline="") as fh:
    records = list(csv.DictReader(fh))

def values(field):
    return [float(record[field]) for record in records]

def percentile_inc(data, p):
    """Inclusive quartile interpolation (like Google Sheets QUARTILE)."""
    data = sorted(data)
    idx = (len(data) - 1) * p
    left, right = math.floor(idx), math.ceil(idx)
    return data[left] + (idx - left) * (data[right] - data[left])

payments = values("payments")
sessions = values("sessions")
q1, q3 = percentile_inc(payments, .25), percentile_inc(payments, .75)
iqr = q3 - q1
low_bound = q1 - 1.5 * iqr
high_bound = q3 + 1.5 * iqr
normal = [x for x in payments if low_bound <= x <= high_bound]
outliers = [x for x in payments if x < low_bound or x > high_bound]
high = [x for x in payments if x > high_bound]
low = [x for x in payments if x < low_bound]
mean_all = statistics.mean(payments)
mean_normal = statistics.mean(normal)

print(f"Users: {len(records)}")
print(f"Payments Q1 / Q3 / IQR: {q1:.2f} / {q3:.2f} / {iqr:.2f}")
print(f"Payment boundaries: {low_bound:.2f} to {high_bound:.2f}")
print(f"High outliers: {len(high)}; low outliers: {len(low)}")
print(f"Average payment, all users: {mean_all:.2f}")
print(f"Average payment, excluding outliers: {mean_normal:.2f}")
print(f"Change in average: {(mean_all - mean_normal) / mean_all * 100:.1f}%")
print(f"Share of total payments from high outliers: {sum(high) / sum(payments) * 100:.1f}%")

plt.figure(figsize=(7.5,4.3))
plt.hist(payments, bins=24, edgecolor="white")
plt.axvline(high_bound, linestyle="--", label=f"IQR upper bound: {high_bound:.2f}")
plt.xlabel("Payment amount (dataset units)")
plt.ylabel("Number of users")
plt.title("Distribution of payments")
plt.legend()
plt.tight_layout()
plt.savefig(CHARTS / "payments_histogram.png", dpi=160)
plt.close()

plt.figure(figsize=(6.5,4.2))
bars = plt.bar(["All 500 users", "477 non-outlier users"], [mean_all, mean_normal])
for bar, val in zip(bars, [mean_all, mean_normal]):
    plt.text(bar.get_x() + bar.get_width()/2, val + .12, f"{val:.2f}", ha="center")
plt.ylim(0,12)
plt.ylabel("Mean payment amount")
plt.title("Average payments with and without outliers")
plt.tight_layout()
plt.savefig(CHARTS / "average_comparison.png", dpi=160)
plt.close()

plt.figure(figsize=(6.5,4.2))
plt.boxplot(sessions, vert=False, tick_labels=["Sessions"])
plt.xlabel("Number of sessions")
plt.title("Sessions: quartiles and outliers")
plt.tight_layout()
plt.savefig(CHARTS / "sessions_boxplot.png", dpi=160)
plt.close()

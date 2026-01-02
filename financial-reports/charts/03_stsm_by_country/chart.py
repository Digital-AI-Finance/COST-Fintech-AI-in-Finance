"""STSM Distribution by Country - Bar Chart"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

plt.rcParams.update({
    'font.size': 12, 'axes.labelsize': 12, 'axes.titlesize': 14,
    'xtick.labelsize': 11, 'ytick.labelsize': 11, 'legend.fontsize': 11,
    'figure.figsize': (10, 6), 'figure.dpi': 150
})

COST_PURPLE = '#5B2D8A'
COST_BLUE = '#2B5F9E'
COST_ORANGE = '#E87722'

# STSM data: host and home country counts
host_data = {'DE': 6, 'IT': 4, 'RO': 3, 'CZ': 3, 'GB': 2, 'NL': 1, 'UK': 1, 'EL': 1, 'ES': 1, 'FR': 1, 'HR': 1, 'PT': 2, 'SK': 1}
home_data = {'RO': 4, 'CH': 5, 'GB': 4, 'IT': 3, 'NO': 2, 'DE': 2, 'FR': 2, 'TR': 2, 'HR': 1, 'DK': 1, 'LT': 1, 'AL': 1, 'IE': 1}

# Combine and get unique countries
all_countries = sorted(set(list(host_data.keys()) + list(home_data.keys())))

host_counts = [host_data.get(c, 0) for c in all_countries]
home_counts = [home_data.get(c, 0) for c in all_countries]

# Sort by total
combined = list(zip(all_countries, host_counts, home_counts))
combined.sort(key=lambda x: x[1] + x[2], reverse=True)
combined = combined[:12]  # Top 12

countries = [c[0] for c in combined]
host = [c[1] for c in combined]
home = [c[2] for c in combined]

x = np.arange(len(countries))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))

bars1 = ax.bar(x - width/2, host, width, label='Host Country', color=COST_PURPLE)
bars2 = ax.bar(x + width/2, home, width, label='Home Country', color=COST_BLUE)

ax.set_xlabel('Country Code')
ax.set_ylabel('Number of STSMs')
ax.set_title('STSM Distribution by Country (27 Total STSMs)')
ax.set_xticks(x)
ax.set_xticklabels(countries)
ax.legend(loc='upper right', framealpha=0.9)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars1:
    height = bar.get_height()
    if height > 0:
        ax.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)

for bar in bars2:
    height = bar.get_height()
    if height > 0:
        ax.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig(Path(__file__).parent / 'chart.pdf', dpi=300, bbox_inches='tight')
plt.savefig(Path(__file__).parent / 'chart.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart saved: 03_stsm_by_country")

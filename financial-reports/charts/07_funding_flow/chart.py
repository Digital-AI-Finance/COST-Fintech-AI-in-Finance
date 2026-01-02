"""Funding Flow by Grant Period and Activity - Stacked Area Chart"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

plt.rcParams.update({
    'font.size': 14, 'axes.labelsize': 14, 'axes.titlesize': 16,
    'xtick.labelsize': 13, 'ytick.labelsize': 13, 'legend.fontsize': 11,
    'figure.figsize': (10, 6), 'figure.dpi': 150
})

COST_PURPLE = '#5B2D8A'
COST_BLUE = '#2B5F9E'
COST_TEAL = '#00A0B0'
COST_ORANGE = '#E87722'
COST_GREEN = '#7AB800'

# Cumulative funding data by activity type
gps = ['Start', 'GP1', 'GP2', 'GP3', 'GP4', 'GP5']
x = np.arange(len(gps))

# Cumulative values in thousands
meetings = [0, 10.3, 32.4, 144.0, 255.3, 376.1]
training = [0, 0, 0, 0, 49.4, 108.8]
stsm = [0, 20.8, 20.8, 44.9, 55.4, 60.0]
virtual = [0, 4.0, 10.8, 16.8, 52.8, 95.3]
other = [0, 12.4, 17.3, 41.8, 87.5, 126.1]

fig, ax = plt.subplots(figsize=(10, 6))

ax.fill_between(x, 0, meetings, alpha=0.8, color=COST_PURPLE, label='Meetings')
ax.fill_between(x, meetings, [m+t for m,t in zip(meetings, training)], alpha=0.8, color=COST_BLUE, label='Training Schools')
ax.fill_between(x, [m+t for m,t in zip(meetings, training)],
                [m+t+s for m,t,s in zip(meetings, training, stsm)], alpha=0.8, color=COST_TEAL, label='STSMs')
ax.fill_between(x, [m+t+s for m,t,s in zip(meetings, training, stsm)],
                [m+t+s+v for m,t,s,v in zip(meetings, training, stsm, virtual)], alpha=0.8, color=COST_ORANGE, label='Virtual Mobility')
ax.fill_between(x, [m+t+s+v for m,t,s,v in zip(meetings, training, stsm, virtual)],
                [m+t+s+v+o for m,t,s,v,o in zip(meetings, training, stsm, virtual, other)], alpha=0.8, color=COST_GREEN, label='Other (ITC, FSAC, etc.)')

ax.set_xlabel('Grant Period')
ax.set_ylabel('Cumulative Expenditure (EUR thousands)')
ax.set_title('COST Action CA19130 - Cumulative Funding Flow (2020-2024)')
ax.set_xticks(x)
ax.set_xticklabels(gps)
ax.legend(loc='upper left', framealpha=0.9)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Add total annotation
total = meetings[-1] + training[-1] + stsm[-1] + virtual[-1] + other[-1]
ax.annotate(f'Total: {total:.1f}K EUR', xy=(5, total), xytext=(4.5, total+30),
            arrowprops=dict(arrowstyle='->', color='gray'), fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig(Path(__file__).parent / 'chart.pdf', dpi=300, bbox_inches='tight')
plt.savefig(Path(__file__).parent / 'chart.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart saved: 07_funding_flow")

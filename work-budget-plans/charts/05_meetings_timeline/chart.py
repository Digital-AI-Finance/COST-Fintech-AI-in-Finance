"""Meetings Timeline - Scatter Plot"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
from pathlib import Path

plt.rcParams.update({
    'font.size': 12, 'axes.labelsize': 12, 'axes.titlesize': 14,
    'xtick.labelsize': 10, 'ytick.labelsize': 10, 'legend.fontsize': 10,
    'figure.figsize': (12, 6), 'figure.dpi': 150
})

COST_PURPLE = '#5B2D8A'
COST_BLUE = '#2B5F9E'
COST_TEAL = '#00A0B0'
COST_ORANGE = '#E87722'
COST_GREEN = '#7AB800'

# Meeting data (date, participants, type)
meetings = [
    ('2020-11-01', 69, 'MC'), ('2021-02-17', 115, 'MC'), ('2021-09-09', 197, 'Conference'),
    ('2021-10-15', 137, 'WG'), ('2021-10-28', 198, 'MC'),
    ('2022-03-24', 238, 'Workshop'), ('2022-04-08', 254, 'WG'), ('2022-05-05', 315, 'Conference'),
    ('2022-05-16', 225, 'Workshop'), ('2022-06-16', 313, 'Conference'), ('2022-07-06', 317, 'WG'),
    ('2022-08-22', 317, 'Workshop'), ('2022-09-21', 316, 'Workshop'), ('2022-09-30', 590, 'Conference'),
    ('2022-10-05', 316, 'MC'), ('2022-10-10', 612, 'WG'), ('2022-10-21', 613, 'Workshop'),
    ('2022-10-28', 290, 'WG'),
    ('2023-02-01', 570, 'Workshop'), ('2023-04-13', 540, 'Workshop'), ('2023-05-15', 288, 'Workshop'),
    ('2023-06-01', 305, 'Workshop'), ('2023-07-10', 12, 'Workshop'), ('2023-09-03', 318, 'Workshop'),
    ('2023-09-27', 312, 'MC'), ('2023-10-30', 15, 'WG'),
    ('2024-04-24', 280, 'WG'), ('2024-05-14', 31, 'Workshop'), ('2024-05-16', 38, 'Workshop'),
    ('2024-05-17', 19, 'Workshop'), ('2024-05-20', 30, 'Workshop'), ('2024-06-27', 39, 'Workshop'),
    ('2024-07-10', 20, 'Workshop'), ('2024-07-18', 35, 'Workshop'), ('2024-08-27', 20, 'Workshop'),
    ('2024-09-06', 73, 'MC')
]

dates = [datetime.strptime(m[0], '%Y-%m-%d') for m in meetings]
participants = [m[1] for m in meetings]
types = [m[2] for m in meetings]

type_colors = {'MC': COST_PURPLE, 'WG': COST_BLUE, 'Workshop': COST_TEAL, 'Conference': COST_ORANGE}
colors = [type_colors[t] for t in types]
sizes = [max(30, p/3) for p in participants]  # Scale bubble sizes

fig, ax = plt.subplots(figsize=(12, 6))

for t in ['MC', 'WG', 'Workshop', 'Conference']:
    mask = [tp == t for tp in types]
    d = [dates[i] for i, m in enumerate(mask) if m]
    p = [participants[i] for i, m in enumerate(mask) if m]
    s = [sizes[i] for i, m in enumerate(mask) if m]
    ax.scatter(d, p, s=s, c=type_colors[t], alpha=0.7, label=t, edgecolors='white', linewidth=0.5)

ax.set_xlabel('Date')
ax.set_ylabel('Number of Participants')
ax.set_title('COST Action CA19130 - Meeting Timeline (2020-2024)')

ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
plt.xticks(rotation=45, ha='right')

# Add GP shading
gp_periods = [
    (datetime(2020, 11, 1), datetime(2021, 10, 31), 'GP1'),
    (datetime(2021, 11, 1), datetime(2022, 5, 31), 'GP2'),
    (datetime(2022, 6, 1), datetime(2022, 10, 31), 'GP3'),
    (datetime(2022, 11, 1), datetime(2023, 10, 31), 'GP4'),
    (datetime(2023, 11, 1), datetime(2024, 9, 13), 'GP5')
]

for i, (start, end, label) in enumerate(gp_periods):
    alpha = 0.08 if i % 2 == 0 else 0.04
    ax.axvspan(start, end, alpha=alpha, color='gray')
    ax.text(start + (end - start)/2, ax.get_ylim()[1]*0.95, label, ha='center', va='top', fontsize=9, alpha=0.7)

ax.legend(loc='upper right', framealpha=0.9)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', alpha=0.3)
ax.set_ylim(0, 700)

plt.tight_layout()
plt.savefig(Path(__file__).parent / 'chart.pdf', dpi=300, bbox_inches='tight')
plt.savefig(Path(__file__).parent / 'chart.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart saved: 05_meetings_timeline")

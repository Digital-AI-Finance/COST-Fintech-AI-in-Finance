# Original Navigation Patterns - COST CA19130

Backup created: 2026-01-03

## Original Navigation Patterns (5 different patterns)

### Pattern 1: Main Site Navigation
Used by: index.html, leadership.html, mc-members.html, wg-members.html, publications.html, etc.
```
COST CA19130 | Home | Leadership | MC | WG | Publications | Mid-Term | Progress | Final
```

### Pattern 2: Final Report Hub Navigation
Used by: final-report.html, final-achievements.html, final-publications.html, final-impacts.html
```
COST CA19130 | Home | Achievements | Publications | Impacts
```

### Pattern 3: Mid-Term Report Hub Navigation
Used by: midterm-report.html and related pages
```
COST CA19130 | Home | Chair Report (Full) | Public Report | Rapporteur | Final Report (Full) | Comparison
```

### Pattern 4: Comparison Suite Navigation
Used by: comparison-enhanced.html, comparison-action-chair.html, comparison-action-chair-full.html
```
COST CA19130 | Home | Final Report | Mid-Term Report | Basic Comparison | Enhanced Comparison | Report Editor
```

### Pattern 5: Financial/Budget Microsites
Used by: financial-reports/*.html, work-budget-plans/*.html
```
COST CA19130 | Home | Work & Budget | Financial Reports | MC | WG
```

## Files Backed Up
- 34 root HTML files
- 13 financial-reports HTML files
- 9 work-budget-plans HTML files

## Rollback Instructions

### Option 1: Git rollback
```bash
git checkout backup-original-nav-20260103
```

### Option 2: File restore
```bash
cp -r _backup_20260103/*.html ./
cp -r _backup_20260103/financial-reports/*.html ./financial-reports/
cp -r _backup_20260103/work-budget-plans/*.html ./work-budget-plans/
```

/**
 * COST Data Utilities
 * Shared functions for loading and formatting data across all pages
 */

const CostData = {
    // Format currency with commas and 2 decimal places
    formatCurrency: function(num) {
        if (num === null || num === undefined) return '0.00';
        return Number(num).toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    },

    // Format number with commas (no decimals)
    formatNumber: function(num) {
        if (num === null || num === undefined) return '0';
        return Math.round(Number(num)).toLocaleString('en-US');
    },

    // Format percentage
    formatPercent: function(num) {
        if (num === null || num === undefined) return '0%';
        return Math.round(Number(num)) + '%';
    },

    // Format percentage with 1 decimal
    formatPercentPrecise: function(num) {
        if (num === null || num === undefined) return '0.0%';
        return Number(num).toFixed(1) + '%';
    },

    // Calculate utilization percentage
    calcUtilization: function(actual, budget) {
        if (!budget || budget === 0) return 0;
        return (actual / budget) * 100;
    },

    // Get value from nested object using dot notation path
    getByPath: function(obj, path) {
        return path.split('.').reduce((acc, part) => {
            if (acc === null || acc === undefined) return undefined;
            // Handle array notation like [0]
            const match = part.match(/^(\w+)\[(\d+)\]$/);
            if (match) {
                return acc[match[1]] ? acc[match[1]][parseInt(match[2])] : undefined;
            }
            return acc[part];
        }, obj);
    },

    // Load JSON file with caching
    cache: {},
    loadJSON: async function(path) {
        if (this.cache[path]) {
            return this.cache[path];
        }
        try {
            const response = await fetch(path);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            this.cache[path] = data;
            return data;
        } catch (error) {
            console.error(`Failed to load ${path}:`, error);
            return null;
        }
    },

    // Update element with data-source attribute
    updateElement: function(element, value, format = 'number') {
        let formatted;
        switch (format) {
            case 'currency':
                formatted = this.formatCurrency(value);
                break;
            case 'percent':
                formatted = this.formatPercent(value);
                break;
            case 'percent-precise':
                formatted = this.formatPercentPrecise(value);
                break;
            default:
                formatted = this.formatNumber(value);
        }
        element.textContent = formatted;
    },

    // Process all elements with data-source attributes
    processDataSources: async function() {
        const elements = document.querySelectorAll('[data-source]');
        const dataFiles = {};

        // Collect unique data files needed
        for (const el of elements) {
            const source = el.dataset.source;
            const file = source.split('.')[0];
            if (!dataFiles[file]) {
                dataFiles[file] = await this.loadJSON(`../data/${file}.json`);
            }
        }

        // Update each element
        for (const el of elements) {
            const source = el.dataset.source;
            const format = el.dataset.format || 'number';
            const [file, ...pathParts] = source.split('.');
            const path = pathParts.join('.');

            if (dataFiles[file]) {
                const value = this.getByPath(dataFiles[file], path);
                if (value !== undefined) {
                    this.updateElement(el, value, format);
                }
            }
        }
    }
};

// Auto-initialize on DOM ready
if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', function() {
        // Only process if there are data-source elements
        if (document.querySelector('[data-source]')) {
            CostData.processDataSources();
        }
    });
}

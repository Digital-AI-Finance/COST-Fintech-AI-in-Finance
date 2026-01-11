/**
 * Verification Overlay System
 * Highlights numbers on page with verification status and enables manual checking
 */

(function() {
    'use strict';

    // Configuration
    const REPORT_PATH = '/COST-Fintech-AI-in-Finance/reports/html_number_verification.json';
    const STORAGE_KEY = 'verifyManualChecks';
    const ENABLED_KEY = 'verifyOverlayEnabled';

    // State
    let verificationData = null;
    let pageData = null;
    let manualChecks = {};
    let overlayEnabled = false;
    let tooltip = null;
    let currentNumber = null;

    // Get current page path relative to site root
    function getCurrentPagePath() {
        const path = window.location.pathname;
        // Handle both local and GitHub Pages paths
        const match = path.match(/(?:COST-Fintech-AI-in-Finance\/)?(.+\.html)$/);
        return match ? match[1] : path.replace(/^\//, '');
    }

    // Load verification report
    async function loadVerificationData() {
        try {
            // Try relative paths for local development
            const paths = [
                REPORT_PATH,
                '../reports/html_number_verification.json',
                '../../reports/html_number_verification.json',
                './reports/html_number_verification.json'
            ];

            for (const path of paths) {
                try {
                    const response = await fetch(path);
                    if (response.ok) {
                        verificationData = await response.json();
                        return true;
                    }
                } catch (e) {
                    continue;
                }
            }
            console.warn('Verification data not found');
            return false;
        } catch (error) {
            console.error('Error loading verification data:', error);
            return false;
        }
    }

    // Get data for current page
    function getPageData() {
        if (!verificationData) return null;

        const currentPath = getCurrentPagePath();
        const pageEntry = verificationData.files.find(f =>
            currentPath.endsWith(f.file) || f.file.endsWith(currentPath)
        );

        return pageEntry || null;
    }

    // Load manual checks from localStorage
    function loadManualChecks() {
        try {
            const stored = localStorage.getItem(STORAGE_KEY);
            manualChecks = stored ? JSON.parse(stored) : {};
        } catch (e) {
            manualChecks = {};
        }
    }

    // Save manual checks to localStorage
    function saveManualChecks() {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(manualChecks));
        } catch (e) {
            console.warn('Could not save to localStorage');
        }
    }

    // Generate unique key for a number
    function getNumberKey(file, line, value) {
        return `${file}:${line}:${value}`;
    }

    // Check if number is manually verified
    function isManuallyChecked(file, line, value) {
        const key = getNumberKey(file, line, value);
        return manualChecks[key] === true;
    }

    // Toggle manual check
    function toggleManualCheck(file, line, value) {
        const key = getNumberKey(file, line, value);
        if (manualChecks[key]) {
            delete manualChecks[key];
        } else {
            manualChecks[key] = true;
        }
        saveManualChecks();
        updateNumberHighlights();
        updateSummary();
    }

    // Create toggle button
    function createToggleButton() {
        const button = document.createElement('button');
        button.className = 'verify-toggle';
        button.innerHTML = `
            <span>Verify Numbers</span>
            <span class="badge" id="verify-badge">...</span>
        `;
        button.addEventListener('click', toggleOverlay);
        document.body.appendChild(button);
        return button;
    }

    // Create summary panel
    function createSummaryPanel() {
        const panel = document.createElement('div');
        panel.className = 'verify-summary';
        panel.id = 'verify-summary';
        panel.innerHTML = `
            <h4>Verification Status</h4>
            <div class="verify-summary-stats">
                <div class="verify-summary-stat verified">
                    <span class="label">Auto-verified:</span>
                    <span class="value" id="stat-verified">0</span>
                </div>
                <div class="verify-summary-stat unverified">
                    <span class="label">Unverified:</span>
                    <span class="value" id="stat-unverified">0</span>
                </div>
                <div class="verify-summary-stat manual">
                    <span class="label">Manually OK:</span>
                    <span class="value" id="stat-manual">0</span>
                </div>
            </div>
        `;
        document.body.appendChild(panel);
        return panel;
    }

    // Create tooltip
    function createTooltip() {
        const tip = document.createElement('div');
        tip.className = 'verify-tooltip';
        tip.id = 'verify-tooltip';
        tip.innerHTML = `
            <button class="verify-tooltip-close">&times;</button>
            <div class="verify-tooltip-header">
                <span class="verify-tooltip-value"></span>
                <span class="verify-tooltip-type"></span>
            </div>
            <div class="verify-tooltip-status"></div>
            <div class="verify-tooltip-source"></div>
            <div class="verify-tooltip-context"></div>
            <div class="verify-tooltip-checkbox">
                <input type="checkbox" id="manual-check">
                <label for="manual-check">Mark as manually verified</label>
            </div>
        `;

        tip.querySelector('.verify-tooltip-close').addEventListener('click', hideTooltip);
        tip.querySelector('#manual-check').addEventListener('change', (e) => {
            if (currentNumber) {
                toggleManualCheck(
                    currentNumber.file,
                    currentNumber.line,
                    currentNumber.value
                );
            }
        });

        document.body.appendChild(tip);
        return tip;
    }

    // Show tooltip for a number
    function showTooltip(element, numberData) {
        if (!tooltip) tooltip = createTooltip();

        currentNumber = numberData;

        const isManual = isManuallyChecked(numberData.file, numberData.line, numberData.value);
        const status = isManual ? 'manual-checked' : (numberData.verified ? 'verified' : 'unverified');
        const statusText = isManual ? 'Manually Verified' : (numberData.verified ? 'Auto-Verified' : 'Unverified');

        tooltip.querySelector('.verify-tooltip-value').textContent = numberData.value;
        tooltip.querySelector('.verify-tooltip-type').textContent = numberData.type;

        const statusEl = tooltip.querySelector('.verify-tooltip-status');
        statusEl.className = `verify-tooltip-status ${status}`;
        statusEl.innerHTML = `<strong>${statusText}</strong>`;

        const sourceEl = tooltip.querySelector('.verify-tooltip-source');
        if (numberData.sources && numberData.sources.length > 0) {
            const source = numberData.sources[0];
            sourceEl.textContent = `Source: ${source.file} > ${source.path}`;
            sourceEl.style.display = 'block';
        } else {
            sourceEl.style.display = 'none';
        }

        const contextEl = tooltip.querySelector('.verify-tooltip-context');
        if (numberData.context) {
            contextEl.textContent = numberData.context;
            contextEl.style.display = 'block';
        } else {
            contextEl.style.display = 'none';
        }

        tooltip.querySelector('#manual-check').checked = isManual;

        // Position tooltip
        const rect = element.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();

        let top = rect.bottom + 10;
        let left = rect.left;

        // Adjust if off screen
        if (left + 300 > window.innerWidth) {
            left = window.innerWidth - 320;
        }
        if (top + 200 > window.innerHeight) {
            top = rect.top - 210;
        }

        tooltip.style.top = `${top}px`;
        tooltip.style.left = `${left}px`;
        tooltip.classList.add('visible');
    }

    // Hide tooltip
    function hideTooltip() {
        if (tooltip) {
            tooltip.classList.remove('visible');
            currentNumber = null;
        }
    }

    // Find and highlight numbers on page
    function highlightNumbers() {
        if (!pageData) return;

        // Combine verified and unverified numbers
        const allNumbers = [
            ...(pageData.verified || []).map(n => ({ ...n, verified: true })),
            ...(pageData.unverified || []).map(n => ({ ...n, verified: false }))
        ];

        // Walk the DOM and find text nodes containing numbers
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            {
                acceptNode: function(node) {
                    // Skip script, style, and already processed elements
                    const parent = node.parentElement;
                    if (!parent) return NodeFilter.FILTER_REJECT;
                    const tag = parent.tagName.toLowerCase();
                    if (['script', 'style', 'noscript'].includes(tag)) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    if (parent.classList.contains('verify-number') ||
                        parent.classList.contains('verify-toggle') ||
                        parent.classList.contains('verify-tooltip') ||
                        parent.classList.contains('verify-summary')) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    return NodeFilter.FILTER_ACCEPT;
                }
            }
        );

        const textNodes = [];
        let node;
        while (node = walker.nextNode()) {
            textNodes.push(node);
        }

        // Process each text node
        textNodes.forEach(textNode => {
            const text = textNode.textContent;
            if (!text.trim()) return;

            // Find numbers in this text
            const numberPattern = /\b(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)\b/g;
            let match;
            const matches = [];

            while ((match = numberPattern.exec(text)) !== null) {
                const value = match[1];
                // Find if this number is in our data
                const numberData = allNumbers.find(n => n.value === value);
                if (numberData) {
                    matches.push({
                        start: match.index,
                        end: match.index + match[0].length,
                        value: value,
                        data: { ...numberData, file: pageData.file }
                    });
                }
            }

            if (matches.length === 0) return;

            // Build new content with spans
            const fragment = document.createDocumentFragment();
            let lastIndex = 0;

            matches.forEach(m => {
                // Add text before match
                if (m.start > lastIndex) {
                    fragment.appendChild(document.createTextNode(text.substring(lastIndex, m.start)));
                }

                // Create span for number
                const span = document.createElement('span');
                span.className = 'verify-number';
                span.textContent = m.value;
                span.dataset.verifyData = JSON.stringify(m.data);

                // Apply status class
                const isManual = isManuallyChecked(m.data.file, m.data.line, m.data.value);
                if (isManual) {
                    span.classList.add('manual-checked');
                } else if (m.data.verified) {
                    span.classList.add('verified');
                } else {
                    span.classList.add('unverified');
                }

                span.addEventListener('click', (e) => {
                    e.stopPropagation();
                    showTooltip(span, m.data);
                });

                fragment.appendChild(span);
                lastIndex = m.end;
            });

            // Add remaining text
            if (lastIndex < text.length) {
                fragment.appendChild(document.createTextNode(text.substring(lastIndex)));
            }

            // Replace text node
            textNode.parentNode.replaceChild(fragment, textNode);
        });
    }

    // Update number highlights based on current state
    function updateNumberHighlights() {
        document.querySelectorAll('.verify-number').forEach(span => {
            try {
                const data = JSON.parse(span.dataset.verifyData);
                const isManual = isManuallyChecked(data.file, data.line, data.value);

                span.classList.remove('verified', 'unverified', 'manual-checked');
                if (isManual) {
                    span.classList.add('manual-checked');
                } else if (data.verified) {
                    span.classList.add('verified');
                } else {
                    span.classList.add('unverified');
                }
            } catch (e) {}
        });
    }

    // Update summary panel
    function updateSummary() {
        if (!pageData) return;

        const verifiedCount = (pageData.verified || []).length;
        const unverifiedRaw = (pageData.unverified || []).length;

        // Count manual checks for this page
        let manualCount = 0;
        const allNumbers = [
            ...(pageData.verified || []),
            ...(pageData.unverified || [])
        ];
        allNumbers.forEach(n => {
            if (isManuallyChecked(pageData.file, n.line, n.value)) {
                manualCount++;
            }
        });

        // Unverified minus manual checks
        const unverifiedCount = Math.max(0, unverifiedRaw - manualCount);

        document.getElementById('stat-verified').textContent = verifiedCount;
        document.getElementById('stat-unverified').textContent = unverifiedCount;
        document.getElementById('stat-manual').textContent = manualCount;

        // Update badge
        const badge = document.getElementById('verify-badge');
        if (badge) {
            badge.textContent = unverifiedCount > 0 ? unverifiedCount : 'OK';
        }
    }

    // Toggle overlay
    function toggleOverlay() {
        overlayEnabled = !overlayEnabled;

        const button = document.querySelector('.verify-toggle');
        const summary = document.getElementById('verify-summary');

        if (overlayEnabled) {
            button.classList.add('active');
            summary.classList.add('visible');
            document.body.classList.remove('verify-overlay-hidden');
            highlightNumbers();
        } else {
            button.classList.remove('active');
            summary.classList.remove('visible');
            document.body.classList.add('verify-overlay-hidden');
            hideTooltip();
        }

        try {
            localStorage.setItem(ENABLED_KEY, overlayEnabled);
        } catch (e) {}
    }

    // Close tooltip when clicking elsewhere
    document.addEventListener('click', (e) => {
        if (tooltip && !tooltip.contains(e.target) && !e.target.classList.contains('verify-number')) {
            hideTooltip();
        }
    });

    // Initialize
    async function init() {
        // Load data
        const loaded = await loadVerificationData();
        if (!loaded) {
            console.log('Verification overlay: No data available');
            return;
        }

        pageData = getPageData();
        if (!pageData) {
            console.log('Verification overlay: No data for this page');
            return;
        }

        loadManualChecks();

        // Create UI elements
        createToggleButton();
        createSummaryPanel();
        tooltip = createTooltip();

        // Update initial state
        updateSummary();

        // Check if was previously enabled
        try {
            overlayEnabled = localStorage.getItem(ENABLED_KEY) === 'true';
            if (overlayEnabled) {
                toggleOverlay();
            }
        } catch (e) {}

        console.log(`Verification overlay initialized for ${pageData.file}`);
    }

    // Start when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

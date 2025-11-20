TOOLTIP_JS = '''
<script>
    let currentTooltip = null;
    let tooltipCache = {};
    let tooltipTimeout = null;
    
    async function fetchTooltipData(word) {
        // Check cache first
        if (tooltipCache[word]) {
            return tooltipCache[word];
        }
        
        try {
            const response = await fetch(`/api/tooltip/${encodeURIComponent(word)}`);
            if (response.ok) {
                const data = await response.json();
                tooltipCache[word] = data;
                return data;
            }
        } catch (error) {
            console.error('Error fetching tooltip:', error);
        }
        return null;
    }
    
    async function showTooltip(element, word) {
        // Clear any pending hide timeout
        if (tooltipTimeout) {
            clearTimeout(tooltipTimeout);
            tooltipTimeout = null;
        }
        
        // Hide current tooltip if different element
        if (currentTooltip && currentTooltip !== element) {
            hideTooltip();
        }
        
        // Check if tooltip already exists
        let tooltip = element.querySelector('.tooltip-content');
        if (!tooltip) {
            // Create tooltip container
            tooltip = document.createElement('div');
            tooltip.className = 'tooltip-content';
            tooltip.innerHTML = '<div class="loading">Loading...</div>';
            element.appendChild(tooltip);
            
            // Fetch data
            const data = await fetchTooltipData(word);
            
            if (data) {
                // Build tooltip content
                let html = `<div class="tooltip-description">${data.description}</div>`;
                html += '<div class="tooltip-links">';
                for (const link of data.links) {
                    html += `<a href="${link.url}" target="_blank" class="tooltip-link">${link.text}</a>`;
                }
                html += '</div>';
                tooltip.innerHTML = html;
            } else {
                tooltip.innerHTML = '<div class="loading">No information available</div>';
            }
            
            // Keep tooltip visible when hovering over it
            tooltip.addEventListener('mouseenter', () => {
                if (tooltipTimeout) {
                    clearTimeout(tooltipTimeout);
                    tooltipTimeout = null;
                }
            });
            
            tooltip.addEventListener('mouseleave', () => {
                tooltipTimeout = setTimeout(hideTooltip, 300);
            });
        }
        
        // Show tooltip
        tooltip.classList.add('active');
        currentTooltip = element;
    }
    
    function hideTooltip() {
        if (currentTooltip) {
            const tooltip = currentTooltip.querySelector('.tooltip-content');
            if (tooltip) {
                tooltip.classList.remove('active');
            }
            currentTooltip = null;
        }
    }
    
    function initTooltips() {
        // Find all tooltip words and add event listeners
        document.querySelectorAll('.tooltip-word').forEach(element => {
            const word = element.dataset.word;
            
            element.addEventListener('mouseenter', () => {
                showTooltip(element, word);
            });
            
            element.addEventListener('mouseleave', () => {
                // Add delay before hiding to allow moving to tooltip
                tooltipTimeout = setTimeout(hideTooltip, 300);
            });
        });
    }
    
    // Initialize tooltips when DOM is ready
    document.addEventListener('DOMContentLoaded', initTooltips);
    
    // Reinitialize after dynamic content changes
    const observer = new MutationObserver(() => {
        initTooltips();
    });
    observer.observe(document.body, { childList: true, subtree: true });
</script>
'''
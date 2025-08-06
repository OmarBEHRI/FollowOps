/**
 * Global Search Functionality
 * Handles search dropdown with suggestions across Projects, Resources, and Tickets
 */

class GlobalSearch {
    constructor(inputId, dropdownId) {
        this.searchInput = document.getElementById(inputId);
        this.searchDropdown = document.getElementById(dropdownId);
        this.searchTimeout = null;
        this.isDropdownVisible = false;
        
        if (this.searchInput) {
            this.init();
        }
    }
    
    init() {
        // Create dropdown if it doesn't exist
        if (!this.searchDropdown) {
            this.createDropdown();
        }
        
        // Bind events
        this.searchInput.addEventListener('input', (e) => this.handleInput(e));
        this.searchInput.addEventListener('focus', (e) => this.handleFocus(e));
        this.searchInput.addEventListener('keydown', (e) => this.handleKeydown(e));
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => this.handleOutsideClick(e));
    }
    
    createDropdown() {
        const dropdownId = `${this.searchInput.id}-dropdown`;
        this.searchDropdown = document.createElement('div');
        this.searchDropdown.id = dropdownId;
        this.searchDropdown.className = 'global-search-dropdown';
        this.searchDropdown.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: #FFFFFF;
            border: 1px solid #EBE5E0;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
            max-height: 400px;
            overflow-y: auto;
            z-index: 1000;
            display: none;
        `;
        
        // Insert dropdown after the search input's parent
        const searchContainer = this.searchInput.closest('label') || this.searchInput.parentElement;
        searchContainer.style.position = 'relative';
        searchContainer.appendChild(this.searchDropdown);
    }
    
    handleInput(e) {
        const query = e.target.value.trim();
        
        // Clear previous timeout
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        
        // Debounce search
        this.searchTimeout = setTimeout(() => {
            if (query.length >= 2) {
                this.performSearch(query);
            } else {
                this.hideDropdown();
            }
        }, 300);
    }
    
    handleFocus(e) {
        const query = e.target.value.trim();
        if (query.length >= 2) {
            this.performSearch(query);
        }
    }
    
    handleKeydown(e) {
        if (!this.isDropdownVisible) return;
        
        const items = this.searchDropdown.querySelectorAll('.search-result-item');
        let currentIndex = -1;
        
        // Find currently selected item
        items.forEach((item, index) => {
            if (item.classList.contains('selected')) {
                currentIndex = index;
            }
        });
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectItem(items, currentIndex + 1);
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.selectItem(items, currentIndex - 1);
                break;
            case 'Enter':
                e.preventDefault();
                if (currentIndex >= 0 && items[currentIndex]) {
                    items[currentIndex].click();
                }
                break;
            case 'Escape':
                this.hideDropdown();
                this.searchInput.blur();
                break;
        }
    }
    
    selectItem(items, index) {
        // Remove previous selection
        items.forEach(item => item.classList.remove('selected'));
        
        // Add selection to new item
        if (index >= 0 && index < items.length) {
            items[index].classList.add('selected');
            items[index].scrollIntoView({ block: 'nearest' });
        }
    }
    
    handleOutsideClick(e) {
        if (!this.searchInput.contains(e.target) && !this.searchDropdown.contains(e.target)) {
            this.hideDropdown();
        }
    }
    
    async performSearch(query) {
        try {
            const response = await fetch(`/projects/api/global-search/?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (data.results && data.results.length > 0) {
                this.displayResults(data.results);
                this.showDropdown();
            } else {
                this.displayNoResults();
                this.showDropdown();
            }
        } catch (error) {
            console.error('Search error:', error);
            this.hideDropdown();
        }
    }
    
    displayResults(results) {
        const groupedResults = this.groupResultsByType(results);
        let html = '';
        
        Object.keys(groupedResults).forEach(type => {
            if (groupedResults[type].length > 0) {
                html += `<div class="search-group">`;
                html += `<div class="search-group-header">${this.getTypeLabel(type)}</div>`;
                
                groupedResults[type].forEach(result => {
                    html += this.createResultItem(result);
                });
                
                html += `</div>`;
            }
        });
        
        this.searchDropdown.innerHTML = html;
    }
    
    displayNoResults() {
        this.searchDropdown.innerHTML = `
            <div class="search-no-results">
                <div style="padding: 16px; text-align: center; color: #6b7280;">
                    Aucun résultat trouvé
                </div>
            </div>
        `;
    }
    
    groupResultsByType(results) {
        return results.reduce((groups, result) => {
            if (!groups[result.type]) {
                groups[result.type] = [];
            }
            groups[result.type].push(result);
            return groups;
        }, {});
    }
    
    getTypeLabel(type) {
        const labels = {
            'project': 'Projets',
            'resource': 'Ressources',
            'ticket': 'Tickets'
        };
        return labels[type] || type;
    }
    
    createResultItem(result) {
        const statusColor = this.getStatusColor(result.status);
        const priorityColor = this.getPriorityColor(result.priority);
        
        return `
            <div class="search-result-item" data-url="${result.url}" onclick="window.location.href='${result.url}'">
                <div class="result-content">
                    <div class="result-header">
                        <span class="result-title">${result.title}</span>
                        <div class="result-badges">
                            ${result.status ? `<span class="status-badge" style="background-color: ${statusColor}">${result.status}</span>` : ''}
                            ${result.priority ? `<span class="priority-badge" style="background-color: ${priorityColor}">${result.priority}</span>` : ''}
                        </div>
                    </div>
                    <div class="result-description">${result.description}</div>
                </div>
            </div>
        `;
    }
    
    getStatusColor(status) {
        const colors = {
            'À initier': '#f59e0b',
            'En cours': '#3b82f6',
            'Terminé': '#10b981',
            'Suspendu': '#f97316',
            'Annulé': '#ef4444',
            'Ouvert': '#f59e0b',
            'Résolu': '#10b981',
            'Fermé': '#6b7280',
            'CDI': '#10b981',
            'CDD': '#f59e0b',
            'Stagiaire': '#8b5cf6',
            'Prestataire': '#06b6d4'
        };
        return colors[status] || '#6b7280';
    }
    
    getPriorityColor(priority) {
        const colors = {
            'Basse': '#10b981',
            'Moyenne': '#f59e0b',
            'Haute': '#f97316',
            'Critique': '#ef4444'
        };
        return colors[priority] || '#6b7280';
    }
    
    showDropdown() {
        this.searchDropdown.style.display = 'block';
        this.isDropdownVisible = true;
    }
    
    hideDropdown() {
        this.searchDropdown.style.display = 'none';
        this.isDropdownVisible = false;
    }
}

// CSS Styles for the dropdown
const globalSearchStyles = `
.global-search-dropdown {
    font-family: inherit;
}

.search-group {
    border-bottom: 1px solid #EBE5E0;
}

.search-group:last-child {
    border-bottom: none;
}

.search-group-header {
    padding: 8px 16px;
    background-color: #FBF9F7;
    font-weight: 600;
    font-size: 12px;
    color: #3F3C3A;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.search-result-item {
    padding: 12px 16px;
    cursor: pointer;
    border-bottom: 1px solid #EBE5E0;
    transition: background-color 0.15s ease;
}

.search-result-item:hover,
.search-result-item.selected {
    background-color: #F1EFE9;
}

.search-result-item:last-child {
    border-bottom: none;
}

.result-content {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
}

.result-title {
    font-weight: 500;
    color: #3F3C3A;
    font-size: 14px;
}

.result-badges {
    display: flex;
    gap: 4px;
    flex-shrink: 0;
}

.status-badge,
.priority-badge {
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 500;
    color: white;
    text-transform: uppercase;
    letter-spacing: 0.025em;
}

.result-description {
    font-size: 12px;
    color: #6E6864;
    line-height: 1.4;
}

.search-no-results {
    padding: 16px;
    text-align: center;
    color: #9C9591;
}
`;

// Inject styles
if (!document.getElementById('global-search-styles')) {
    const styleSheet = document.createElement('style');
    styleSheet.id = 'global-search-styles';
    styleSheet.textContent = globalSearchStyles;
    document.head.appendChild(styleSheet);
}

// Export for use
window.GlobalSearch = GlobalSearch;
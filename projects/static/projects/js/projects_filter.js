// JavaScript for handling filter dropdowns and search functionality
document.addEventListener('DOMContentLoaded', function() {
  // Status dropdown
  const statusBtn = document.getElementById('status-dropdown-btn');
  const statusDropdown = document.getElementById('status-dropdown');
  
  statusBtn.addEventListener('click', function() {
    statusDropdown.classList.toggle('hidden');
    priorityDropdown.classList.add('hidden');
    projectManagerDropdown.classList.add('hidden');
  });
  
  // Priority dropdown
  const priorityBtn = document.getElementById('priority-dropdown-btn');
  const priorityDropdown = document.getElementById('priority-dropdown');
  
  priorityBtn.addEventListener('click', function() {
    priorityDropdown.classList.toggle('hidden');
    statusDropdown.classList.add('hidden');
    projectManagerDropdown.classList.add('hidden');
  });
  
  // Project Manager dropdown
  const projectManagerBtn = document.getElementById('project-manager-dropdown-btn');
  const projectManagerDropdown = document.getElementById('project-manager-dropdown');
  
  projectManagerBtn.addEventListener('click', function() {
    projectManagerDropdown.classList.toggle('hidden');
    statusDropdown.classList.add('hidden');
    priorityDropdown.classList.add('hidden');
  });
  
  // Close dropdowns when clicking outside
  document.addEventListener('click', function(event) {
    if (!statusBtn.contains(event.target) && !statusDropdown.contains(event.target)) {
      statusDropdown.classList.add('hidden');
    }
    
    if (!priorityBtn.contains(event.target) && !priorityDropdown.contains(event.target)) {
      priorityDropdown.classList.add('hidden');
    }
    
    if (!projectManagerBtn.contains(event.target) && !projectManagerDropdown.contains(event.target)) {
      projectManagerDropdown.classList.add('hidden');
    }
  });

  // Search functionality
  // Enhanced Search functionality with suggestions
  const searchInput = document.getElementById('search-input');
  const suggestionsContainer = document.getElementById('search-suggestions');
  const suggestionsList = document.getElementById('suggestions-list');
  const noSuggestions = document.getElementById('no-suggestions');
  const projectsTableBody = document.getElementById('projects-table-body');
  
  let searchTimeout = null;
  let currentSuggestionIndex = -1;
  
  if (searchInput && suggestionsContainer) {
    
    // Function to perform fuzzy search
    // Function to perform fuzzy search
    function fuzzyMatch(text, query) {
      const textLower = text.toLowerCase();
      const queryLower = query.toLowerCase();
      
      // For single character searches, just check if text starts with or contains the character
      if (queryLower.length === 1) {
        return textLower.includes(queryLower);
      }
      
      // Exact match gets highest score
      if (textLower.includes(queryLower)) {
        return true;
      }
      
      // Simple fuzzy matching for typos (only for queries of 2+ characters)
      let textIndex = 0;
      let queryIndex = 0;
      let matches = 0;
      
      while (textIndex < textLower.length && queryIndex < queryLower.length) {
        if (textLower[textIndex] === queryLower[queryIndex]) {
          matches++;
          queryIndex++;
        }
        textIndex++;
      }
      
      // Allow for some typos (at least 70% of characters should match)
      return matches >= Math.ceil(queryLower.length * 0.7);
    }
    
    // Function to fetch suggestions from API
    function fetchSuggestions(query) {
      // Permettre la recherche dès 1 caractère au lieu de 2
      if (query.length < 1) {
        hideSuggestions();
        return;
      }
      
      fetch(`/projects/api/search-suggestions/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
          displaySuggestions(data.suggestions, query);
        })
        .catch(error => {
          console.error('Erreur lors de la récupération des suggestions:', error);
          hideSuggestions();
        });
    }
    
    // Function to display suggestions
    function displaySuggestions(suggestions, query) {
      suggestionsList.innerHTML = '';
      currentSuggestionIndex = -1;
      
      if (suggestions.length === 0) {
        noSuggestions.classList.remove('hidden');
        suggestionsList.classList.add('hidden');
      } else {
        noSuggestions.classList.add('hidden');
        suggestionsList.classList.remove('hidden');
        
        suggestions.forEach((suggestion, index) => {
          const suggestionElement = createSuggestionElement(suggestion, query, index);
          suggestionsList.appendChild(suggestionElement);
        });
      }
      
      suggestionsContainer.classList.remove('hidden');
    }
    
    // Function to create suggestion element
    function createSuggestionElement(suggestion, query, index) {
      const div = document.createElement('div');
      div.className = 'px-4 py-3 hover:bg-gray-100 cursor-pointer border-b border-gray-100 last:border-b-0';
      div.dataset.index = index;
      div.dataset.url = suggestion.url;
      
      // Highlight matching text
      const highlightedTitle = highlightMatch(suggestion.title, query);
      const highlightedDescription = highlightMatch(suggestion.description, query);
      
      div.innerHTML = `
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <div class="font-medium text-gray-900">${highlightedTitle}</div>
            <div class="text-sm text-gray-600 mt-1">${highlightedDescription}</div>
            <div class="flex items-center gap-2 mt-2">
              <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                ${suggestion.status}
              </span>
              <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                ${suggestion.priority}
              </span>
              <span class="text-xs text-gray-500">${suggestion.manager}</span>
            </div>
          </div>
        </div>
      `;
      
      // Add click event
      div.addEventListener('click', function() {
        window.location.href = suggestion.url;
      });
      
      return div;
    }
    
    // Function to highlight matching text
    function highlightMatch(text, query) {
      if (!query) return text;
      
      const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
      return text.replace(regex, '<mark class="bg-yellow-200">$1</mark>');
    }
    
    // Function to hide suggestions
    function hideSuggestions() {
      suggestionsContainer.classList.add('hidden');
      currentSuggestionIndex = -1;
    }
    
    // Search input event listeners
    searchInput.addEventListener('input', function() {
      const query = this.value.trim();
      
      // Filtrer le tableau IMMÉDIATEMENT - pas de délai
      filterTable(query);
      
      // Clear previous timeout pour les suggestions
      if (searchTimeout) {
        clearTimeout(searchTimeout);
      }
      
      // Debounce seulement pour les suggestions API (pas pour le filtrage du tableau)
      searchTimeout = setTimeout(() => {
        if (query.length >= 1) {
          fetchSuggestions(query);
        } else {
          hideSuggestions();
        }
      }, 150);
    });
    
    // Supprimer ou commenter l'événement keydown qui gère Enter
    // pour éviter tout comportement de soumission de formulaire
    searchInput.addEventListener('keydown', function(e) {
      const suggestions = suggestionsList.querySelectorAll('[data-index]');
      
      switch(e.key) {
        case 'ArrowDown':
          e.preventDefault();
          currentSuggestionIndex = Math.min(currentSuggestionIndex + 1, suggestions.length - 1);
          updateSuggestionHighlight(suggestions);
          break;
          
        case 'ArrowUp':
          e.preventDefault();
          currentSuggestionIndex = Math.max(currentSuggestionIndex - 1, -1);
          updateSuggestionHighlight(suggestions);
          break;
          
        case 'Enter':
          e.preventDefault(); // Empêcher la soumission du formulaire
          if (currentSuggestionIndex >= 0 && suggestions[currentSuggestionIndex]) {
            // Aller à la suggestion sélectionnée
            const selectedSuggestion = suggestions[currentSuggestionIndex];
            const url = selectedSuggestion.querySelector('a')?.href;
            if (url) {
              window.location.href = url;
            }
          }
          // Ne pas soumettre le formulaire - juste garder le filtrage actuel
          break;
          
        case 'Escape':
          hideSuggestions();
          this.blur();
          break;
      }
    });
    
    // Function to update suggestion highlight
    function updateSuggestionHighlight(suggestions) {
      suggestions.forEach((suggestion, index) => {
        if (index === currentSuggestionIndex) {
          suggestion.classList.add('bg-gray-100');
        } else {
          suggestion.classList.remove('bg-gray-100');
        }
      });
    }
    
    // Function to filter table (version corrigée)
    function filterTable(searchTerm) {
      if (!projectsTableBody) return;
      
      const rows = projectsTableBody.querySelectorAll('tr');
      let visibleCount = 0;
      const searchTermLower = searchTerm.toLowerCase();
      
      rows.forEach(function(row) {
        // Skip the "no projects found" row if it exists
        if (row.cells.length === 1 && row.cells[0].colSpan) {
          return;
        }
        
        // Cache les données pour éviter les requêtes DOM répétées
        if (!row._searchData) {
          // CORRECTION: Le titre est directement dans la cellule, pas dans un lien
          const titleElement = row.querySelector('td:first-child');
          const descElement = row.querySelector('td:nth-child(2)');
          const typeElement = row.querySelector('td:nth-child(3) span');
          const statusElement = row.querySelector('td:nth-child(4) span');
          const priorityElement = row.querySelector('td:nth-child(5) span');
          const managerElement = row.querySelector('td:nth-child(6)');
          
          row._searchData = {
            title: titleElement?.textContent.toLowerCase() || '',
            description: descElement?.textContent.toLowerCase() || '',
            type: typeElement?.textContent.toLowerCase() || '',
            status: statusElement?.textContent.toLowerCase() || '',
            priority: priorityElement?.textContent.toLowerCase() || '',
            manager: managerElement?.textContent.toLowerCase() || ''
          };
        }
        
        const data = row._searchData;
        const isVisible = searchTerm === '' || 
            data.title.includes(searchTermLower) || 
            data.description.includes(searchTermLower) || 
            data.type.includes(searchTermLower) || 
            data.status.includes(searchTermLower) || 
            data.priority.includes(searchTermLower) || 
            data.manager.includes(searchTermLower);
        
        if (isVisible) {
          row.style.display = '';
          visibleCount++;
        } else {
          row.style.display = 'none';
        }
      });
      
      // Gérer le message "aucun résultat"
      const existingNoResultsRow = projectsTableBody.querySelector('.no-results-row');
      if (existingNoResultsRow) {
        existingNoResultsRow.remove();
      }
      
      if (visibleCount === 0 && searchTerm !== '') {
        const noResultsRow = document.createElement('tr');
        noResultsRow.className = 'no-results-row';
        noResultsRow.innerHTML = `<td colspan="8" class="px-4 py-5 text-center text-[#8c7e5a]">Aucun projet trouvé pour "${searchTerm}"</td>`;
        projectsTableBody.appendChild(noResultsRow);
      }
    }
    
    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
      if (!searchInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
        hideSuggestions();
      }
    });
    
    // Focus event to show suggestions if there's a query
    searchInput.addEventListener('focus', function() {
      const query = this.value.trim();
      if (query.length >= 2) {
        fetchSuggestions(query);
      }
    });
  }
  
  // Clear search when filters are applied
  const filterLinks = document.querySelectorAll('#status-dropdown a, #priority-dropdown a, #project-manager-dropdown a');
  filterLinks.forEach(function(link) {
    link.addEventListener('click', function() {
      // Store the search term in session storage before navigating
      if (searchInput.value) {
        sessionStorage.setItem('projectSearchTerm', searchInput.value);
      }
    });
  });
  
  // Check if there's a stored search term and apply it
  const storedSearchTerm = sessionStorage.getItem('projectSearchTerm');
  if (storedSearchTerm) {
    searchInput.value = storedSearchTerm;
    // Trigger the input event to filter the table
    const inputEvent = new Event('input');
    searchInput.dispatchEvent(inputEvent);
    // Clear the stored search term
    sessionStorage.removeItem('projectSearchTerm');
  }
});
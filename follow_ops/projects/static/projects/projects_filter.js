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
  const searchInput = document.getElementById('search-input');
  const projectsTableBody = document.getElementById('projects-table-body');
  
  if (searchInput && projectsTableBody) {
    searchInput.addEventListener('input', function() {
      const searchTerm = this.value.toLowerCase().trim();
      const rows = projectsTableBody.querySelectorAll('tr');
      
      rows.forEach(function(row) {
        // Skip the "no projects found" row if it exists
        if (row.cells.length === 1 && row.cells[0].colSpan) {
          return;
        }
        
        const projectTitle = row.querySelector('td:first-child a')?.textContent.toLowerCase() || '';
        const projectDescription = row.querySelector('td:nth-child(2)')?.textContent.toLowerCase() || '';
        const projectType = row.querySelector('td:nth-child(3) span')?.textContent.toLowerCase() || '';
        const projectStatus = row.querySelector('td:nth-child(4) span')?.textContent.toLowerCase() || '';
        const projectPriority = row.querySelector('td:nth-child(5) span')?.textContent.toLowerCase() || '';
        const projectManager = row.querySelector('td:nth-child(6)')?.textContent.toLowerCase() || '';
        
        if (searchTerm === '' || 
            projectTitle.includes(searchTerm) || 
            projectDescription.includes(searchTerm) || 
            projectType.includes(searchTerm) || 
            projectStatus.includes(searchTerm) || 
            projectPriority.includes(searchTerm) || 
            projectManager.includes(searchTerm)) {
          row.style.display = '';
        } else {
          row.style.display = 'none';
        }
      });
      
      // Check if all rows are hidden, then show a "no results" message
      let allHidden = true;
      rows.forEach(function(row) {
        if (row.style.display !== 'none' && row.cells.length > 1) {
          allHidden = false;
        }
      });
      
      // If there's already a "no results" row, remove it first
      const existingNoResults = projectsTableBody.querySelector('.no-results-row');
      if (existingNoResults) {
        existingNoResults.remove();
      }
      
      if (allHidden && searchTerm !== '') {
        const noResultsRow = document.createElement('tr');
        noResultsRow.className = 'no-results-row border-t border-t-[#e3dfd3]';
        noResultsRow.innerHTML = '<td colspan="8" class="px-4 py-5 text-center text-[#8c7e5a]">Aucun projet trouvé pour "' + searchTerm + '"</td>';
        projectsTableBody.appendChild(noResultsRow);
      }
    });
    
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
  }
});
// JavaScript for handling filter dropdowns and search functionality
document.addEventListener('DOMContentLoaded', function() {
  // Status dropdown
  const statusBtn = document.getElementById('status-dropdown-btn');
  const statusDropdown = document.getElementById('status-dropdown');
  
  statusBtn.addEventListener('click', function() {
    statusDropdown.classList.toggle('hidden');
    priorityDropdown.classList.add('hidden');
  });
  
  // Priority dropdown
  const priorityBtn = document.getElementById('priority-dropdown-btn');
  const priorityDropdown = document.getElementById('priority-dropdown');
  
  priorityBtn.addEventListener('click', function() {
    priorityDropdown.classList.toggle('hidden');
    statusDropdown.classList.add('hidden');
  });
  
  // Close dropdowns when clicking outside
  document.addEventListener('click', function(event) {
    if (!statusBtn.contains(event.target) && !statusDropdown.contains(event.target)) {
      statusDropdown.classList.add('hidden');
    }
    
    if (!priorityBtn.contains(event.target) && !priorityDropdown.contains(event.target)) {
      priorityDropdown.classList.add('hidden');
    }
  });
});
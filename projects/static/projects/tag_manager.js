// Tag Manager for Project Form
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const addTagBtn = document.getElementById('add-tag-btn');
    const tagSearchContainer = document.getElementById('tag-search-container');
    const tagSearch = document.getElementById('tag-search');
    const tagSearchResults = document.getElementById('tag-search-results');
    const selectedTagsContainer = document.getElementById('selected-tags-container');
    const tagsSelect = document.getElementById('id_tags');
    
    // Show search input when add button is clicked
    addTagBtn.addEventListener('click', function() {
        tagSearchContainer.classList.remove('hidden');
        tagSearch.focus();
    });
    
    // Handle tag search input
    tagSearch.addEventListener('input', function() {
        const searchTerm = this.value.trim();
        
        if (searchTerm.length < 2) {
            tagSearchResults.classList.add('hidden');
            return;
        }
        
        // Fetch matching tags from server
        fetch(`/projects/api/tags/search/?term=${encodeURIComponent(searchTerm)}`)
            .then(response => response.json())
            .then(data => {
                tagSearchResults.innerHTML = '';
                
                if (data.tags.length > 0) {
                    data.tags.forEach(tag => {
                        const tagElement = document.createElement('div');
                        tagElement.className = 'p-2 hover:bg-[#f7f5f3] cursor-pointer';
                        tagElement.textContent = tag.name;
                        tagElement.dataset.id = tag.id;
                        
                        tagElement.addEventListener('click', function() {
                            addTag(tag.id, tag.name);
                            tagSearch.value = '';
                            tagSearchResults.classList.add('hidden');
                        });
                        
                        tagSearchResults.appendChild(tagElement);
                    });
                    
                    tagSearchResults.classList.remove('hidden');
                } else {
                    // Show option to create new tag
                    const createTagElement = document.createElement('div');
                    createTagElement.className = 'p-2 hover:bg-[#f7f5f3] cursor-pointer text-[#A08D80] font-medium';
                    createTagElement.textContent = `Créer "${searchTerm}"`;
                    
                    createTagElement.addEventListener('click', function() {
                        createNewTag(searchTerm);
                    });
                    
                    tagSearchResults.appendChild(createTagElement);
                    tagSearchResults.classList.remove('hidden');
                }
            })
            .catch(error => {
                console.error('Error searching tags:', error);
            });
    });
    
    // Handle Enter key in search input
    tagSearch.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const searchTerm = this.value.trim();
            
            if (searchTerm.length > 0) {
                createNewTag(searchTerm);
            }
        }
    });
    
    // Close search results when clicking outside
    document.addEventListener('click', function(e) {
        if (!tagSearchContainer.contains(e.target) && e.target !== addTagBtn) {
            tagSearchResults.classList.add('hidden');
            
            // Only hide search container if it's empty
            if (tagSearch.value.trim() === '') {
                tagSearchContainer.classList.add('hidden');
            }
        }
    });
    
    // Function to add a tag to the selected tags
    function addTag(id, name) {
        // Check if tag is already selected
        if (isTagSelected(id)) {
            return;
        }
        
        // Create tag element
        const tagElement = document.createElement('div');
        tagElement.className = 'bg-[#eae6df] text-[#191610] px-3 py-1 rounded-full flex items-center';
        tagElement.dataset.id = id;
        
        tagElement.innerHTML = `
            <span>${name}</span>
            <button type="button" class="ml-2 text-[#6E6864] hover:text-[#191610]">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </button>
        `;
        
        // Add remove event listener
        const removeBtn = tagElement.querySelector('button');
        removeBtn.addEventListener('click', function() {
            removeTag(id);
            tagElement.remove();
        });
        
        // Add to container
        selectedTagsContainer.appendChild(tagElement);
        
        // Update hidden select
        updateTagsSelect(id, true);
    }
    
    // Function to remove a tag
    function removeTag(id) {
        updateTagsSelect(id, false);
    }
    
    // Function to check if a tag is already selected
    function isTagSelected(id) {
        return selectedTagsContainer.querySelector(`[data-id="${id}"]`) !== null;
    }
    
    // Function to update the hidden select element
    function updateTagsSelect(id, selected) {
        // Find the option
        const option = Array.from(tagsSelect.options).find(opt => opt.value == id);
        
        if (option) {
            option.selected = selected;
        } else if (selected) {
            // If the option doesn't exist yet (new tag), it will be added by the server
            // We'll add a temporary option
            const newOption = new Option('', id, false, true);
            tagsSelect.appendChild(newOption);
        }
    }
    
    // Function to create a new tag
    function createNewTag(name) {
        fetch('/projects/api/tags/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ name: name })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                addTag(data.tag.id, data.tag.name);
                tagSearch.value = '';
                tagSearchResults.classList.add('hidden');
            } else {
                console.error('Error creating tag:', data.error);
            }
        })
        .catch(error => {
            console.error('Error creating tag:', error);
        });
    }
    
    // Function to get CSRF token
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
    
    // Load existing tags if editing a project
    function loadExistingTags() {
        // Check if tagsSelect exists before trying to access its properties
        if (!tagsSelect) {
            console.error('Tags select element not found');
            return;
        }
        
        // Get selected options from the hidden select
        const selectedOptions = tagsSelect.selectedOptions ? Array.from(tagsSelect.selectedOptions) : [];
        
        selectedOptions.forEach(option => {
            addTag(option.value, option.textContent);
        });
    }
    
    // Initialize
    loadExistingTags();
});
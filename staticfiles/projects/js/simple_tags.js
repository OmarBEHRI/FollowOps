// Gestion simple des tags
class SimpleTags {
    constructor() {
        this.input = document.getElementById('tag-input');
        this.display = document.getElementById('selected-tags');
        this.hiddenInput = document.getElementById('id_tags');
        this.tags = new Set();
        
        this.init();
    }
    
    init() {
        // Écouter l'entrée de texte
        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ',') {
                e.preventDefault();
                this.addTag(this.input.value.trim());
                this.input.value = '';
            }
        });
        
        // Ajouter au blur
        this.input.addEventListener('blur', () => {
            if (this.input.value.trim()) {
                this.addTag(this.input.value.trim());
                this.input.value = '';
            }
        });
    }
    
    addTag(tagName) {
        if (!tagName || this.tags.has(tagName)) return;
        
        this.tags.add(tagName);
        this.renderTags();
        this.updateHiddenInput();
    }
    
    removeTag(tagName) {
        this.tags.delete(tagName);
        this.renderTags();
        this.updateHiddenInput();
    }
    
    renderTags() {
        this.display.innerHTML = '';
        
        this.tags.forEach(tag => {
            const tagEl = document.createElement('span');
            tagEl.className = 'simple-tag';
            tagEl.innerHTML = `
                ${tag}
                <button type="button" class="tag-remove" onclick="simpleTags.removeTag('${tag}')">
                    ×
                </button>
            `;
            this.display.appendChild(tagEl);
        });
    }
    
    updateHiddenInput() {
        this.hiddenInput.value = Array.from(this.tags).join(',');
    }
}

// Initialiser
let simpleTags;
document.addEventListener('DOMContentLoaded', () => {
    simpleTags = new SimpleTags();
});
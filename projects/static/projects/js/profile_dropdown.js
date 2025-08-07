class ProfileDropdown {
    constructor() {
        this.init();
    }

    init() {
        this.createDropdownStyles();
        this.setupEventListeners();
    }

    createDropdownStyles() {
        // Check if styles already exist
        if (document.getElementById('profile-dropdown-styles')) {
            return;
        }

        const styles = `
            .profile-dropdown-container {
                position: relative;
                display: inline-block;
            }

            .profile-dropdown-menu {
                position: absolute;
                top: 100%;
                right: 0;
                background: #FFFFFF;
                border: 1px solid #EBE5E0;
                border-radius: 12px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                min-width: 160px;
                z-index: 1000;
                opacity: 0;
                visibility: hidden;
                transform: translateY(-10px);
                transition: all 0.2s ease-in-out;
                margin-top: 8px;
            }

            .profile-dropdown-menu.show {
                opacity: 1;
                visibility: visible;
                transform: translateY(0);
            }

            .profile-dropdown-item {
                display: flex;
                align-items: center;
                padding: 12px 16px;
                color: #3F3C3A;
                text-decoration: none;
                font-size: 14px;
                font-weight: 500;
                border-bottom: 1px solid #F5F3F0;
                transition: background-color 0.15s ease;
                cursor: pointer;
            }

            .profile-dropdown-item:last-child {
                border-bottom: none;
            }

            .profile-dropdown-item:hover {
                background-color: #F5F3F0;
                color: #2D2A27;
            }

            .profile-dropdown-item:first-child {
                border-radius: 12px 12px 0 0;
            }

            .profile-dropdown-item:last-child {
                border-radius: 0 0 12px 12px;
            }

            .profile-dropdown-item:only-child {
                border-radius: 12px;
            }

            .profile-dropdown-icon {
                width: 16px;
                height: 16px;
                margin-right: 8px;
                flex-shrink: 0;
            }

            .profile-picture {
                cursor: pointer;
                transition: transform 0.2s ease;
            }

            .profile-picture:hover {
                transform: scale(1.05);
            }
        `;

        const styleSheet = document.createElement('style');
        styleSheet.id = 'profile-dropdown-styles';
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }

    setupEventListeners() {
        document.addEventListener('click', (e) => {
            const profilePicture = e.target.closest('.profile-picture');
            const dropdown = e.target.closest('.profile-dropdown-container');
            
            if (profilePicture) {
                e.preventDefault();
                e.stopPropagation();
                this.toggleDropdown(profilePicture);
            } else if (!dropdown) {
                this.closeAllDropdowns();
            }
        });

        // Close dropdown on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllDropdowns();
            }
        });
    }

    toggleDropdown(profilePicture) {
        const container = profilePicture.closest('.profile-dropdown-container');
        const menu = container.querySelector('.profile-dropdown-menu');
        
        // Close other dropdowns first
        this.closeAllDropdowns();
        
        // Toggle current dropdown
        if (menu) {
            menu.classList.toggle('show');
        }
    }

    closeAllDropdowns() {
        const allMenus = document.querySelectorAll('.profile-dropdown-menu');
        allMenus.forEach(menu => {
            menu.classList.remove('show');
        });
    }

    getCurrentUserId() {
        // Try to get user ID from various sources
        const userIdMeta = document.querySelector('meta[name="user-id"]');
        if (userIdMeta) {
            return userIdMeta.getAttribute('content');
        }
        
        // Fallback: try to get from localStorage or other sources
        const storedUserId = localStorage.getItem('userId');
        if (storedUserId) {
            return storedUserId;
        }
        
        // Default fallback
        return '1';
    }

    handleViewProfile() {
        const userId = this.getCurrentUserId();
        window.location.href = `/ressources/details/${userId}`;
    }

    handleLogout() {
        // Clear localStorage
        localStorage.clear();
        
        // Call Django logout
        fetch('/logout/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.getCSRFToken(),
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        })
        .then(() => {
            // Redirect to root
            window.location.href = '/';
        })
        .catch((error) => {
            console.error('Logout error:', error);
            // Still redirect even if logout fails
            window.location.href = '/';
        });
    }

    getCSRFToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            return csrfToken.value;
        }
        
        const csrfCookie = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='));
        
        return csrfCookie ? csrfCookie.split('=')[1] : '';
    }

    createDropdownHTML() {
        return `
            <div class="profile-dropdown-menu">
                <a href="#" class="profile-dropdown-item" onclick="window.profileDropdown.handleViewProfile(); return false;">
                    <svg class="profile-dropdown-icon" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                    </svg>
                    View Profile
                </a>
                <a href="#" class="profile-dropdown-item" onclick="window.profileDropdown.handleLogout(); return false;">
                    <svg class="profile-dropdown-icon" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.59L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/>
                    </svg>
                    Logout
                </a>
            </div>
        `;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.profileDropdown = new ProfileDropdown();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProfileDropdown;
}
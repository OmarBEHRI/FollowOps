// Project Calendar JavaScript Module
class ProjectCalendar {
    constructor(config) {
        this.config = config;
        this.currentMonth = config.currentMonth;
        this.currentYear = config.currentYear;
        this.currentDate = new Date(this.currentYear, this.currentMonth - 1, 1);
        this.selectedDay = null;
        this.selectedDayDate = null; // Store the full date for day view
        this.isMonthView = true;
        this.projectActivities = config.projectActivities || [];
        
        this.initializeElements();
        this.bindEvents();
        this.renderCalendar();
    }

    initializeElements() {
        this.calendarContainer = document.getElementById('calendar-container');
        this.calendarGrid = document.getElementById('calendar-grid');
        this.monthYearDisplay = document.getElementById('month-year-display');
        this.prevMonthBtn = document.getElementById('prevMonthProject');
        this.nextMonthBtn = document.getElementById('nextMonthProject');
        this.backToMonthBtn = document.getElementById('back-to-month');
        this.addActivityBtn = document.getElementById('add-activity-btn');
        this.dayView = document.getElementById('day-view');
        this.dayViewContent = document.getElementById('day-view-content');
        
        // Modal elements
        this.addActivityModal = document.getElementById('addActivityModal');
        this.closeAddActivityModal = document.getElementById('closeAddActivityModal');
        this.cancelAddActivity = document.getElementById('cancelAddActivity');
        this.addActivityForm = document.getElementById('addActivityForm');
    }

    bindEvents() {
        // Navigation events - now handles both month and day navigation
        this.prevMonthBtn?.addEventListener('click', () => this.navigate(-1));
        this.nextMonthBtn?.addEventListener('click', () => this.navigate(1));
        this.backToMonthBtn?.addEventListener('click', () => this.showMonthView());

        // Modal events
        this.addActivityBtn?.addEventListener('click', (e) => this.openAddActivityModal(e));
        this.closeAddActivityModal?.addEventListener('click', () => this.closeModal());
        this.cancelAddActivity?.addEventListener('click', () => this.closeModal());
        
        // Close modal when clicking outside
        this.addActivityModal?.addEventListener('click', (e) => {
            if (e.target === this.addActivityModal) {
                this.closeModal();
            }
        });

        // Form submission
        this.addActivityForm?.addEventListener('submit', (e) => this.handleFormSubmission(e));
    }

    // Helper function to convert hex to RGB
    hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    }

    // Generate calendar
    renderCalendar() {
        console.log('renderCalendar called');
        if (!this.calendarGrid) {
            console.error('calendarGrid not found');
            return;
        }
        this.calendarGrid.innerHTML = '';

        // Add day headers
        const dayNames = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];
        dayNames.forEach(day => {
            const dayHeader = document.createElement('div');
            dayHeader.className = 'calendar-day-header';
            dayHeader.textContent = day;
            this.calendarGrid.appendChild(dayHeader);
        });

        // Determine first day of month
        const firstDay = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), 1);
        const startingDay = firstDay.getDay() || 7;
        const daysInMonth = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1, 0).getDate();

        // Add empty cells for days before first day of month
        for (let i = 1; i < startingDay; i++) {
            const emptyCell = document.createElement('div');
            emptyCell.className = 'calendar-cell inactive';
            this.calendarGrid.appendChild(emptyCell);
        }

        // Add cells for each day of the month
        const today = new Date();
        console.log('Creating cells for', daysInMonth, 'days');
        for (let day = 1; day <= daysInMonth; day++) {
            const cell = document.createElement('div');
            cell.className = 'calendar-cell';

            // Check if it's today
            if (day === today.getDate() &&
                this.currentDate.getMonth() === today.getMonth() &&
                this.currentDate.getFullYear() === today.getFullYear()) {
                cell.classList.add('today');
            }

            // Add date to cell
            const dateSpan = document.createElement('span');
            dateSpan.className = 'calendar-date';
            dateSpan.textContent = day;
            cell.appendChild(dateSpan);

            // Container for activities
            const activitiesContainer = document.createElement('div');
            activitiesContainer.className = 'activities-container';

            // Check activities for this day (including multi-day activities)
            const cellDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), day);
            const activitiesOnDay = this.projectActivities.filter(activity => {
                const activityStartDate = new Date(activity.startDate);
                const activityEndDate = new Date(activity.endDate);

                // Normalize dates to compare only days (without hours)
                const cellDateOnly = new Date(cellDate.getFullYear(), cellDate.getMonth(), cellDate.getDate());
                const startDateOnly = new Date(activityStartDate.getFullYear(), activityStartDate.getMonth(), activityStartDate.getDate());
                const endDateOnly = new Date(activityEndDate.getFullYear(), activityEndDate.getMonth(), activityEndDate.getDate());

                // Activity is displayed if cell day is between start and end of activity (inclusive)
                return cellDateOnly >= startDateOnly && cellDateOnly <= endDateOnly;
            });

            // Display activities (maximum 3 visible)
            const maxVisible = 3;
            activitiesOnDay.slice(0, maxVisible).forEach(activity => {
                const activityItem = document.createElement('div');
                activityItem.className = 'activity-item';
                activityItem.textContent = activity.title;

                // Apply member-specific color to the entire activity item
                if (activity.employee_color) {
                    activityItem.style.background = activity.employee_color;
                    activityItem.style.borderLeftColor = activity.employee_color;
                    activityItem.style.border = `2px solid ${activity.employee_color}`;

                    // Adjust text color based on background brightness
                    const rgb = this.hexToRgb(activity.employee_color);
                    const brightness = (rgb.r * 299 + rgb.g * 587 + rgb.b * 114) / 1000;
                    activityItem.style.color = brightness > 128 ? '#000000' : '#FFFFFF';
                } else {
                    // Fallback to default styling
                    activityItem.className += ' inprogress';
                }

                // Add tooltip
                const tooltip = document.createElement('div');
                tooltip.className = 'activity-tooltip';
                tooltip.innerHTML = `
                    <div class="activity-tooltip-title">${activity.title}</div>
                    <div class="activity-tooltip-info">Assigné à: ${activity.employee}</div>
                    <div class="activity-tooltip-info">Charge: ${activity.charge} heures</div>
                    <div class="activity-tooltip-description">${activity.description}</div>
                `;
                activityItem.appendChild(tooltip);

                activitiesContainer.appendChild(activityItem);
            });

            // Show "+ X others" if there are more activities
            if (activitiesOnDay.length > maxVisible) {
                const moreActivities = document.createElement('div');
                moreActivities.className = 'more-activities';
                moreActivities.textContent = `+ ${activitiesOnDay.length - maxVisible} autres`;
                activitiesContainer.appendChild(moreActivities);
            }

            cell.appendChild(activitiesContainer);

            // Add click event for day view
            cell.addEventListener('click', () => {
                this.showDayView(day, activitiesOnDay);
            });

            this.calendarGrid.appendChild(cell);
        }
    }

    // Show day view
    showDayView(day, activities = null) {
        this.selectedDay = day;
        this.selectedDayDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), day);
        this.isMonthView = false;

        // Hide calendar grid and show day view
        this.calendarGrid.classList.add('hidden');
        this.dayView.classList.remove('hidden');
        this.backToMonthBtn.classList.remove('hidden');
        this.addActivityBtn.classList.add('hidden');

        // Update main header to show the current day
        this.updateHeaderForDayView();

        // If activities not provided, get them for the selected day
        if (activities === null) {
            activities = this.getActivitiesForDay(this.selectedDayDate);
        }

        // Generate day view content
        this.renderDayViewContent(activities);
    }

    // Update header for day view
    updateHeaderForDayView() {
        const dayText = this.selectedDayDate.toLocaleDateString('fr-FR', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        // Capitalize first letter
        this.monthYearDisplay.textContent = dayText.charAt(0).toUpperCase() + dayText.slice(1);
    }

    // Get activities for a specific day
    getActivitiesForDay(dayDate) {
        return this.projectActivities.filter(activity => {
            const activityStartDate = new Date(activity.startDate);
            const activityEndDate = new Date(activity.endDate);

            // Normalize dates to compare only days (without hours)
            const dayDateOnly = new Date(dayDate.getFullYear(), dayDate.getMonth(), dayDate.getDate());
            const startDateOnly = new Date(activityStartDate.getFullYear(), activityStartDate.getMonth(), activityStartDate.getDate());
            const endDateOnly = new Date(activityEndDate.getFullYear(), activityEndDate.getMonth(), activityEndDate.getDate());

            // Activity is displayed if the day is between start and end of activity (inclusive)
            return dayDateOnly >= startDateOnly && dayDateOnly <= endDateOnly;
        });
    }

    // Render day view content
    renderDayViewContent(activities) {
        this.dayViewContent.innerHTML = '';

        // Create time slots
        for (let hour = 9; hour <= 20; hour++) {
            const hourLabel = document.createElement('div');
            hourLabel.className = 'hour-label';
            hourLabel.textContent = `${hour}:00`;

            const hourActivities = document.createElement('div');
            hourActivities.className = 'hour-activities';

            // Filter activities for this hour
            const hourActivitiesList = activities.filter(activity => {
                const activityHour = new Date(activity.startDate).getHours();
                return activityHour === hour;
            });

            if (hourActivitiesList.length === 0) {
                hourActivities.innerHTML = '';
            } else {
                hourActivitiesList.forEach(activity => {
                    const dayActivity = document.createElement('div');
                    dayActivity.className = 'day-activity';
                    dayActivity.innerHTML = `
                        <div class="day-activity-title">${activity.title}</div>
                        <div class="day-activity-time">${new Date(activity.startDate).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })} - ${new Date(activity.endDate).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}</div>
                        <div class="day-activity-description">${activity.description}</div>
                    `;

                    // Apply member-specific color to day view activities
                    if (activity.employee_color) {
                        dayActivity.style.background = `${activity.employee_color}20`; // 20% opacity
                        dayActivity.style.borderLeftColor = activity.employee_color;
                        dayActivity.style.borderLeftWidth = '4px';

                        // Adjust text color based on background brightness
                        const rgb = this.hexToRgb(activity.employee_color);
                        const brightness = (rgb.r * 299 + rgb.g * 587 + rgb.b * 114) / 1000;
                        dayActivity.style.color = brightness > 128 ? '#000000' : '#333333';
                    } else {
                        // Fallback to default styling
                        dayActivity.className += ' inprogress';
                    }

                    hourActivities.appendChild(dayActivity);
                });
            }

            this.dayViewContent.appendChild(hourLabel);
            this.dayViewContent.appendChild(hourActivities);
        }
    }

    // Show month view
    showMonthView() {
        this.isMonthView = true;
        this.selectedDay = null;
        this.selectedDayDate = null;

        // Show calendar grid and hide day view
        this.calendarGrid.classList.remove('hidden');
        this.dayView.classList.add('hidden');
        this.backToMonthBtn.classList.add('hidden');
        this.addActivityBtn.classList.remove('hidden');

        // Update header back to month view
        this.updateHeaderForMonthView();
    }

    // Update header for month view
    updateHeaderForMonthView() {
        const monthName = this.currentDate.toLocaleDateString('fr-FR', {
            month: 'long',
            year: 'numeric'
        });
        // Capitalize first letter
        this.monthYearDisplay.textContent = monthName.charAt(0).toUpperCase() + monthName.slice(1);
    }

    // Navigate - handles both month and day navigation
    navigate(direction) {
        if (this.isMonthView) {
            this.navigateMonth(direction);
        } else {
            this.navigateDay(direction);
        }
    }

    // Navigate months
    navigateMonth(direction) {
        this.currentDate.setMonth(this.currentDate.getMonth() + direction);
        this.currentMonth = this.currentDate.getMonth() + 1;
        this.currentYear = this.currentDate.getFullYear();
        this.updateHeaderForMonthView();
        this.renderCalendar();
    }

    // Navigate days
    navigateDay(direction) {
        // Move the selected day by the specified direction
        this.selectedDayDate.setDate(this.selectedDayDate.getDate() + direction);
        
        // Update the selected day number
        this.selectedDay = this.selectedDayDate.getDate();
        
        // Check if we moved to a different month
        if (this.selectedDayDate.getMonth() !== this.currentDate.getMonth() || 
            this.selectedDayDate.getFullYear() !== this.currentDate.getFullYear()) {
            // Update current date to match the new month/year
            this.currentDate = new Date(this.selectedDayDate.getFullYear(), this.selectedDayDate.getMonth(), 1);
            this.currentMonth = this.currentDate.getMonth() + 1;
            this.currentYear = this.currentDate.getFullYear();
        }

        // Update header and content for the new day
        this.updateHeaderForDayView();
        const activities = this.getActivitiesForDay(this.selectedDayDate);
        this.renderDayViewContent(activities);
    }

    // Set default form values
    setDefaultFormValues() {
        const today = new Date();

        // Set default start date to today
        document.getElementById('startDate').value = today.toISOString().split('T')[0];
        // Set default end date to today (same day activity by default)
        document.getElementById('endDate').value = today.toISOString().split('T')[0];

        // Set default times
        document.getElementById('startTime').value = '09:00';
        document.getElementById('endTime').value = '10:00';
    }

    // Open add activity modal
    openAddActivityModal(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('Add activity button clicked');

        // Set default form values
        this.setDefaultFormValues();

        // Remove hidden classes and add show class
        this.addActivityModal.classList.remove('hidden');
        this.addActivityModal.classList.add('modal-show');

        // Prevent body scroll
        document.body.style.overflow = 'hidden';
    }

    // Close modal
    closeModal() {
        if (this.addActivityModal) {
            this.addActivityModal.classList.remove('modal-show');
            this.addActivityModal.classList.add('hidden');

            // Restore body scroll
            document.body.style.overflow = '';

            // Reset form
            if (this.addActivityForm) {
                this.addActivityForm.reset();
                this.hideValidationError();
            }
        }
    }

    // Handle form submission
    handleFormSubmission(e) {
        e.preventDefault();

        // Prevent multiple submissions
        const submitBtn = this.addActivityForm.querySelector('button[type="submit"]');
        if (submitBtn.disabled) return;

        // Get form data
        const formData = new FormData(this.addActivityForm);
        const title = formData.get('title');
        const startDate = formData.get('start_date');
        const startTime = formData.get('start_time');
        const endDate = formData.get('end_date');
        const endTime = formData.get('end_time');
        const description = formData.get('description');
        const type = formData.get('type');

        // Validation
        if (!title || !startDate || !startTime || !endDate || !endTime || !description || !type) {
            this.showValidationError('Tous les champs sont obligatoires');
            return;
        }

        if (!this.validateActivityForm(startDate, startTime, endDate, endTime)) {
            return;
        }

        // Build data to send
        const activityData = {
            title: `${type ? '[' + type + '] ' : ''}${title}`,
            description: description,
            activity_type: 'PROJECT',
            start_datetime: `${startDate}T${startTime}:00`,
            end_datetime: `${endDate}T${endTime}:00`,
            project_id: this.config.projectId
        };

        // Disable submit button and show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = `
            <span class="flex items-center justify-center space-x-2">
                <svg class="animate-spin w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                <span>Création...</span>
            </span>
        `;

        // Get CSRF token from the form or cookie
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value || this.getCookie('csrftoken');

        // Send request
        fetch(`/projects/calendar/${this.config.projectId}/create-activity/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(activityData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Success - add activity to local array and reload calendar
                this.projectActivities.push(data.activity);
                this.closeModal();
                this.showNotification('Activité créée avec succès!', 'success');
                this.renderCalendar();
            } else {
                // Error
                this.showValidationError(data.message || 'Erreur lors de la création de l\'activité');
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            this.showValidationError('Erreur lors de la création de l\'activité: ' + error.message);
        })
        .finally(() => {
            // Re-enable submit button
            submitBtn.disabled = false;
            submitBtn.innerHTML = `
                <span class="flex items-center justify-center space-x-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                    </svg>
                    <span>Créer l'activité</span>
                </span>
            `;
        });
    }

    // Utility functions
    validateActivityForm(startDateStr, startTime, endDateStr, endTime) {
        const startDateTime = new Date(`${startDateStr}T${startTime}`);
        const endDateTime = new Date(`${endDateStr}T${endTime}`);

        // Check that end date/time is after start date/time
        if (endDateTime <= startDateTime) {
            this.showValidationError('La date et heure de fin doivent être après la date et heure de début');
            return false;
        }

        // Check that activity doesn't exceed 7 days
        const diffDays = (endDateTime - startDateTime) / (1000 * 60 * 60 * 24);
        if (diffDays > 7) {
            this.showValidationError('Une activité ne peut pas dépasser 7 jours');
            return false;
        }

        // Suppression de la contrainte d'heures de travail (8h-18h)
        return true;
    }

    showValidationError(message) {
        const errorDiv = document.getElementById('validationError');
        const errorText = document.getElementById('validationErrorText');
        if (errorDiv && errorText) {
            errorText.textContent = message;
            errorDiv.classList.remove('hidden');
            // Scroll to error message
            errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    hideValidationError() {
        const errorDiv = document.getElementById('validationError');
        if (errorDiv) {
            errorDiv.classList.add('hidden');
        }
    }

    showNotification(message, type = 'info') {
        // Create notification
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full`;

        if (type === 'success') {
            notification.classList.add('bg-green-500', 'text-white');
        } else if (type === 'error') {
            notification.classList.add('bg-red-500', 'text-white');
        } else {
            notification.classList.add('bg-blue-500', 'text-white');
        }

        notification.textContent = message;
        document.body.appendChild(notification);

        // Animate entry
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Tab functionality (keeping the existing function)
function showTab(tabName) {
    // Hide all tabs
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => {
        if (tab) {
            tab.style.display = 'none';
        }
    });

    // Show selected tab
    const selectedTab = document.getElementById(tabName);
    if (selectedTab) {
        selectedTab.style.display = 'block';
    }

    // Update tab buttons
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        if (button) {
            button.classList.remove('active');
        }
    });

    const activeButton = document.querySelector(`[onclick="showTab('${tabName}')"]`);
    if (activeButton) {
        activeButton.classList.add('active');
    }
}
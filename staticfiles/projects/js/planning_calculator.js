// Calculateur de planning pour les projets
document.addEventListener('DOMContentLoaded', function() {
    const startDateInput = document.getElementById('id_expected_start_date');
    const endDateInput = document.getElementById('id_expected_end_date');
    const durationIndicator = document.getElementById('duration-indicator');
    const calculatedDuration = document.getElementById('calculated-duration');
    
    function calculateDuration() {
        const startDate = new Date(startDateInput.value);
        const endDate = new Date(endDateInput.value);
        
        if (startDate && endDate && startDate < endDate) {
            const timeDiff = endDate.getTime() - startDate.getTime();
            const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));
            
            calculatedDuration.textContent = `${daysDiff} jour${daysDiff > 1 ? 's' : ''}`;
            durationIndicator.style.display = 'block';
        } else {
            durationIndicator.style.display = 'none';
        }
    }
    
    // Écouter les changements de dates
    if (startDateInput && endDateInput) {
        startDateInput.addEventListener('change', calculateDuration);
        endDateInput.addEventListener('change', calculateDuration);
        
        // Calculer au chargement si les dates sont déjà remplies
        calculateDuration();
    }
});
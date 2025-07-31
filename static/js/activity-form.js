// Gestionnaire pour la soumission du formulaire d'activité
document.addEventListener('DOMContentLoaded', function() {
    const addActivityForm = document.getElementById('addActivityForm');
    const addActivityModal = document.getElementById('addActivityModal');
    
    if (addActivityForm) {
        addActivityForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            console.log('Début de la soumission du formulaire');
            
            // Collecter les données du formulaire
            const startDate = document.getElementById('activityStartDate').value;
            const endDate = document.getElementById('activityEndDate').value;
            const title = document.getElementById('activityTitle').value;
            const description = document.getElementById('activityDescription').value;
            const activityType = document.getElementById('activityType').value;
            
            console.log('Données collectées:', {
                title,
                description,
                activityType,
                startDate,
                endDate
            });
            
            // Vérifier que les champs obligatoires sont remplis
            if (!title || !startDate || !endDate) {
                alert('Veuillez remplir tous les champs obligatoires');
                return;
            }
            
            const data = {
                title: title,
                description: description,
                activity_type: activityType,
                start_datetime: startDate,
                end_datetime: endDate,
                resource_id: window.location.pathname.split('/').filter(Boolean).pop()
            };
            
            // Ajouter le projet ou ticket selon le type d'activité
            if (activityType === 'PROJECT') {
                const projectId = document.getElementById('activityProject').value;
                if (projectId) {
                    data.project_id = projectId;
                }
            } else if (activityType === 'TICKET') {
                const ticketId = document.getElementById('activityTicket').value;
                if (ticketId) {
                    data.ticket_id = ticketId;
                }
            }
            
            console.log('Données à envoyer:', data);
            
            // Vérifier le token CSRF
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
            if (!csrfToken) {
                console.error('Token CSRF non trouvé');
                alert('Erreur: Token CSRF manquant');
                return;
            }
            
            console.log('Token CSRF trouvé:', csrfToken.value);
            
            // Envoyer la requête avec JSON au lieu de FormData
            fetch('/activities/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken.value
                },
                body: JSON.stringify(data)
            })
            .then(response => {
                console.log('Statut de la réponse:', response.status);
                console.log('Headers de la réponse:', response.headers);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                return response.json();
            })
            .then(data => {
                console.log('Réponse reçue:', data);
                
                if (data.success) {
                    console.log('Activité créée avec succès');
                    
                    // Fermer le modal
                    if (addActivityModal) {
                        addActivityModal.style.display = 'none';
                    }
                    
                    // Réinitialiser le formulaire
                    addActivityForm.reset();
                    
                    // Masquer les sélections de projet/ticket
                    const projectSelect = document.getElementById('projectSelect');
                    const ticketSelect = document.getElementById('ticketSelect');
                    if (projectSelect) projectSelect.style.display = 'none';
                    if (ticketSelect) ticketSelect.style.display = 'none';
                    
                    // Recharger les activités pour mettre à jour le calendrier
                    if (typeof loadActivities === 'function') {
                        loadActivities();
                    } else {
                        console.warn('Fonction loadActivities non trouvée, rechargement de la page');
                        window.location.reload();
                    }
                    
                    // Afficher un message de succès
                    alert('Activité créée avec succès !');
                } else {
                    console.error('Erreur lors de la création de l\'activité:', data);
                    alert('Erreur lors de la création de l\'activité: ' + (data.message || data.error || 'Erreur inconnue'));
                }
            })
            .catch(error => {
                console.error('Erreur complète:', error);
                console.error('Stack trace:', error.stack);
                alert('Erreur lors de la création de l\'activité: ' + error.message);
            });
        });
    } else {
        console.error('Formulaire addActivityForm non trouvé');
    }
});
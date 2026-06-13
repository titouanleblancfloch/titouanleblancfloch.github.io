// modal.js - Script pour gérer les modals de projet

document.addEventListener('DOMContentLoaded', function() {
    // Sélectionner tous les boutons "Voir le projet"
    const projectButtons = document.querySelectorAll('.view-project');
    
    // Sélectionner tous les boutons de fermeture des modals
    const closeButtons = document.querySelectorAll('.close-modal');
    
    // Ajouter un gestionnaire d'événements à chaque bouton de projet
    projectButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Récupérer l'ID du projet à partir de l'attribut data-project
            const projectId = this.getAttribute('data-project');
            
            // Trouver la modal correspondante
            const modal = document.getElementById(projectId);
            
            // Afficher la modal
            if (modal) {
                modal.classList.add('show');
                document.body.style.overflow = 'hidden'; // Empêcher le défilement du body
            }
        });
    });
    
    // Ajouter un gestionnaire d'événements à chaque bouton de fermeture
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Trouver la modal parente
            const modal = this.closest('.modal');
            
            // Fermer la modal
            if (modal) {
                modal.classList.remove('show');
                document.body.style.overflow = ''; // Réactiver le défilement du body
            }
        });
    });
    
    // Fermer la modal en cliquant en dehors du contenu
    window.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal') && e.target.classList.contains('show')) {
            e.target.classList.remove('show');
            document.body.style.overflow = ''; // Réactiver le défilement du body
        }
    });
    
    // Fermer la modal avec la touche Echap
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                openModal.classList.remove('show');
                document.body.style.overflow = ''; // Réactiver le défilement du body
            }
        }
    });
});
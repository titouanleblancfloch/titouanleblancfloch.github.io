// main.js - Scripts communs pour toutes les pages

// Attendre que le DOM soit complètement chargé
document.addEventListener('DOMContentLoaded', function() {
    // Définir la page active dans le menu de navigation
    setActiveNavLink();
    
    // Initialiser le menu burger pour mobile
    initBurgerMenu();
});

// Fonction pour définir le lien actif dans la navigation
function setActiveNavLink() {
    // Obtenir le nom de fichier actuel (ex: index.html, about.html, etc.)
    const currentPage = window.location.pathname.split('/').pop();
    
    // Sélectionner tous les liens de navigation
    const navLinks = document.querySelectorAll('nav ul li a');
    
    // Parcourir tous les liens et définir la classe active pour la page courante
    navLinks.forEach(link => {
        // Retirer d'abord toutes les classes active
        link.classList.remove('active');
        
        // Définir la classe active sur le lien correspondant à la page actuelle
        if (currentPage === '') {
            // Si nous sommes à la racine, activer le lien vers l'accueil
            if (link.getAttribute('href') === 'index.html') {
                link.classList.add('active');
            }
        } else if (link.getAttribute('href') === currentPage) {
            link.classList.add('active');
        }
    });
}

// Fonction pour initialiser le menu burger sur mobile
function initBurgerMenu() {
    const burgerMenu = document.querySelector('.burger-menu');
    const nav = document.querySelector('nav');
    
    // Si le menu burger existe, ajouter l'écouteur d'événements
    if (burgerMenu) {
        burgerMenu.addEventListener('click', function() {
            // Basculer la classe active sur la navigation
            nav.classList.toggle('active');
        });
        
        // Fermer le menu en cliquant sur un lien
        const navLinks = document.querySelectorAll('nav ul li a');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                nav.classList.remove('active');
            });
        });
        
        // Fermer le menu en cliquant en dehors
        document.addEventListener('click', function(event) {
            const isClickInsideNav = nav.contains(event.target);
            const isClickOnBurger = burgerMenu.contains(event.target);
            
            if (!isClickInsideNav && !isClickOnBurger && nav.classList.contains('active')) {
                nav.classList.remove('active');
            }
        });
    }
}
// main.js - Scripts communs pour toutes les pages

// Attendre que le DOM soit complètement chargé
document.addEventListener('DOMContentLoaded', function() {
    // Définir la page active dans le menu de navigation
    setActiveNavLink();
    
    // Initialiser le menu burger pour mobile
    initBurgerMenu();
    
    // Initialiser les animations spécifiques à la page bilan
    initProgressBars();
    initTimelineAnimation();
    initParallaxEffect();
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

// Animation des barres de progression (spécifique à la page bilan)
function initProgressBars() {
    // Vérifier si nous sommes sur la page bilan
    if (document.querySelector('.skills-progress')) {
        const progressObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const progressBars = entry.target.querySelectorAll('.progress-fill');
                    progressBars.forEach(bar => {
                        // Récupérer le pourcentage depuis l'attribut data-width
                        const targetWidth = bar.getAttribute('data-width');
                        if (targetWidth) {
                            setTimeout(() => {
                                bar.style.width = targetWidth + '%';
                            }, 200);
                        }
                    });
                }
            });
        }, { threshold: 0.5 });

        // Observer toutes les sections de barres de progression
        document.querySelectorAll('.skills-progress').forEach(section => {
            progressObserver.observe(section);
        });
    }
}

// Animation au scroll pour les éléments de la timeline (spécifique à la page bilan)
function initTimelineAnimation() {
    // Vérifier si nous sommes sur la page bilan
    if (document.querySelector('.timeline-item-modern')) {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, observerOptions);

        document.querySelectorAll('.timeline-item-modern').forEach(item => {
            observer.observe(item);
        });
    }
}

// Effet parallax pour les éléments flottants (spécifique à la page bilan)
function initParallaxEffect() {
    // Vérifier si nous sommes sur la page bilan
    if (document.querySelector('.floating-element')) {
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            const parallaxElements = document.querySelectorAll('.floating-element');
            
            parallaxElements.forEach((element, index) => {
                const speed = 0.1 + (index * 0.05);
                element.style.transform = `translateY(${scrolled * speed}px)`;
            });
        });
    }
}

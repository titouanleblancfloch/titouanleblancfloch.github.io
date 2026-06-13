// Charger les données et générer les projets
document.addEventListener('DOMContentLoaded', async () => {
    try {
        let data = null;

        // Essayer d'abord de charger le JSON (priorité aux modifications de projects-data.json)
        const pathsToTry = [
            'projects-data.json',
            '../pages/projects-data.json',
            '/pages/projects-data.json'
        ];

        for (const p of pathsToTry) {
            try {
                const bustUrl = `${p}${p.includes('?') ? '&' : '?'}v=${Date.now()}`;
                const resp = await fetch(bustUrl, { cache: 'no-store' });
                if (!resp.ok) {
                    console.warn(`Échec fetch ${p}: ${resp.status}`);
                    continue;
                }
                data = await resp.json();
                console.log(`Chargé: ${p}`);
                break;
            } catch (e) {
                console.warn(`Erreur fetch ${p}:`, e);
            }
        }

        // Fallback uniquement si le fetch échoue (ex: ouverture en file://)
        if (!data && window.PROJECTS_DATA && window.PROJECTS_DATA.projects) {
            data = window.PROJECTS_DATA;
            console.log('Chargé depuis window.PROJECTS_DATA (fallback)');
        }

        if (!data || !data.projects) {
            throw new Error('Impossible de charger projects-data.json ou format invalide');
        }

        // Générer les cartes de projets pour toutes les années présentes
        Object.keys(data.projects).forEach(yearKey => {
            const containerId = `${yearKey}-projects`;
            generateProjectCards(containerId, data.projects[yearKey] || []);
        });

        // Générer les modales (flat all projects)
        generateModals(data.projects);

        // Attacher les écouteurs d'événements
        attachEventListeners();
    } catch (error) {
        console.error('Erreur lors du chargement des données:', error);
        showInlineError('Impossible de charger les données des projets. Ouvrez la console pour plus de détails.');
    }
});

/**
 * Génère les cartes de projets
 */
function generateProjectCards(containerId, projects) {
    const container = document.getElementById(containerId);
    
    if (!container) {
        console.error(`Container avec l'ID "${containerId}" non trouvé`);
        return;
    }
    // clear existing content (placeholder or stale)
    container.innerHTML = '';

    projects.forEach((project, index) => {
        const card = document.createElement('div');
        card.className = 'project-card';
        
        const techList = (project.technologies || []).join(', ');
        const cardLabel = project.cardLabel || `Projet ${index + 1}`;
        
        card.innerHTML = `
            <div class="project-img">${cardLabel}</div>
            <div class="project-content">
                <h3 class="project-title">${project.title}</h3>
                <p><strong>Technologies:</strong> ${techList}</p>
                <a href="#" class="btn view-project" data-project="${project.id}">Voir le projet</a>
            </div>
        `;
        
        container.appendChild(card);
    });
}

/**
 * Génère les modales
 */
function generateModals(allProjects) {
    const container = document.getElementById('modal-container');
    
    if (!container) {
        console.error('Container modal-container non trouvé');
        return;
    }
    
    // Flatten all year arrays into a single list
    const allProjectsList = Object.values(allProjects).reduce((acc, arr) => acc.concat(arr || []), []);
    
    allProjectsList.forEach(project => {
        const modal = document.createElement('div');
        modal.id = project.id;
        modal.className = 'modal';
        
        // Générer les liens
        let linksHTML = '';
        if (project.links && project.links.length > 0) {
            linksHTML = '<div class="modal-links">';
            project.links.forEach(link => {
                linksHTML += `<a href="${link.url}" target="_blank" class="btn">${link.label}</a>`;
            });
            linksHTML += '</div>';
        }
        
        // Générer les compétences
        let skillsHTML = '';
        if (project.skills && project.skills.length > 0) {
            skillsHTML = '<div class="modal-section"><h3>Compétences mobilisées</h3><ul>';
            project.skills.forEach(skill => {
                skillsHTML += `<li>${skill}</li>`;
            });
            skillsHTML += '</ul></div>';
        }
        
        // Générer les technologies
        let techHTML = '<div class="tags">';
        (project.technologies || []).forEach(tech => {
            techHTML += `<span class="skill-tag">${tech}</span>`;
        });
        techHTML += '</div>';
        
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close-modal">&times;</span>
                <div class="modal-header">
                    <h2>${project.title}</h2>
                </div>
                <div class="modal-body">
                    <div class="modal-details">
                        <div class="modal-section">
                            <h3>Description</h3>
                            <p>${project.description}</p>
                        </div>
                        
                        <div class="modal-section">
                            <h3>Technologies utilisées</h3>
                            ${techHTML}
                        </div>
                        
                        ${skillsHTML}
                        
                        ${project.links && project.links.length > 0 ? `
                        <div class="modal-section">
                            <h3>Liens</h3>
                            ${linksHTML}
                        </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
        
        container.appendChild(modal);
    });
}

/**
 * Attache les écouteurs d'événements pour les modales
 */
function attachEventListeners() {
    // Ouvrir les modales
    document.querySelectorAll('.view-project').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const projectId = btn.getAttribute('data-project');
            const modal = document.getElementById(projectId);
            if (modal) {
                modal.classList.add('show');
                document.body.style.overflow = 'hidden';
            }
        });
    });
    
    // Fermer les modales
    document.querySelectorAll('.close-modal').forEach(closeBtn => {
        closeBtn.addEventListener('click', () => {
            const modal = closeBtn.closest('.modal');
            if (modal) {
                modal.classList.remove('show');
                document.body.style.overflow = '';
            }
        });
    });
    
    // Fermer la modale en cliquant en dehors
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal') && e.target.classList.contains('show')) {
            e.target.classList.remove('show');
            document.body.style.overflow = '';
        }
    });
}

/** Affiche une erreur visible dans la page pour faciliter le debug */
function showInlineError(message) {
    let existing = document.getElementById('projects-error');
    if (existing) return;
    const container = document.querySelector('.container') || document.body;
    const box = document.createElement('div');
    box.id = 'projects-error';
    box.style.background = '#ffe6e6';
    box.style.color = '#800';
    box.style.padding = '12px 16px';
    box.style.border = '1px solid #f5c2c2';
    box.style.margin = '12px 0';
    box.style.borderRadius = '6px';
    box.textContent = message;
    container.insertBefore(box, container.firstChild);
}

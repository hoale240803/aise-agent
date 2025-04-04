document.addEventListener('DOMContentLoaded', () => {
    // Theme Toggle
    const themeToggle = document.querySelector('.theme-toggle');
    const body = document.body;

    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        body.classList.add(savedTheme);
        updateThemeIcon(savedTheme);
    }

    themeToggle.addEventListener('click', () => {
        if (body.classList.contains('dark-mode')) {
            body.classList.remove('dark-mode');
            body.classList.add('light-mode');
            localStorage.setItem('theme', 'light-mode');
        } else {
            body.classList.remove('light-mode');
            body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark-mode');
        }
        updateThemeIcon();
    });

    function updateThemeIcon() {
        const icon = themeToggle.querySelector('i');
        const text = themeToggle.querySelector('span');
        if (body.classList.contains('dark-mode')) {
            icon.classList.remove('fa-sun');
            icon.classList.add('fa-moon');
            text.textContent = 'Dark Mode';
        } else {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
            text.textContent = 'Light Mode';
        }
    }

    // Notification Badge
    const notificationBtn = document.querySelector('.notification-btn');
    const badge = document.querySelector('.badge');

    notificationBtn.addEventListener('click', () => {
        // TODO: Implement notification panel
        badge.style.display = 'none';
    });

    // Quick Action Buttons
    const actionButtons = document.querySelectorAll('.action-btn');
    actionButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const action = e.target.closest('.action-btn');
            if (action) {
                // TODO: Implement action handlers
                console.log('Action clicked:', action.textContent.trim());
            }
        });
    });

    // Project Card Interactions
    const projectCards = document.querySelectorAll('.project-card');
    projectCards.forEach(card => {
        card.addEventListener('click', (e) => {
            if (!e.target.closest('.action-btn')) {
                // TODO: Navigate to project details
                console.log('Project clicked:', card.querySelector('h3').textContent);
            }
        });
    });

    // Search Functionality
    const searchInput = document.querySelector('.search-bar input');
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        // TODO: Implement search functionality
        console.log('Searching for:', searchTerm);
    });

    // Real-time Updates (WebSocket Simulation)
    function simulateRealTimeUpdates() {
        setInterval(() => {
            // TODO: Implement actual WebSocket connection
            updateActivityFeed();
            updateProjectMetrics();
        }, 30000); // Update every 30 seconds
    }

    function updateActivityFeed() {
        const activityFeed = document.querySelector('.activity-feed');
        // TODO: Implement actual activity feed updates
    }

    function updateProjectMetrics() {
        const projectMetrics = document.querySelectorAll('.project-metrics');
        // TODO: Implement actual metric updates
    }

    // Start real-time updates
    simulateRealTimeUpdates();
}); 
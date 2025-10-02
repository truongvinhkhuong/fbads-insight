// Navigation Menu JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Navigation script loaded');
    
    const stickyNav = document.getElementById('sticky-nav');
    const fabNav = document.getElementById('fab-nav');
    const navToggle = document.getElementById('nav-toggle');
    const fabToggle = document.getElementById('fab-toggle');
    const navToggleText = document.getElementById('nav-toggle-text');
    const navLinks = document.querySelectorAll('.nav-link');
    
    console.log('Elements found:', {
        stickyNav: !!stickyNav,
        fabNav: !!fabNav,
        navToggle: !!navToggle,
        fabToggle: !!fabToggle,
        navLinks: navLinks.length
    });
    
    let isMenuOpen = false;
    
    // Toggle menu visibility
    function toggleMenu() {
        console.log('Toggle menu clicked, current state:', isMenuOpen);
        isMenuOpen = !isMenuOpen;
        
        if (isMenuOpen) {
            stickyNav.classList.remove('hidden');
            fabNav.classList.add('hidden');
            navToggleText.textContent = '✕';
            console.log('Menu opened');
        } else {
            stickyNav.classList.add('hidden');
            fabNav.classList.remove('hidden');
            navToggleText.textContent = '☰';
            console.log('Menu closed');
        }
    }
    
    // Smooth scroll to section
    function smoothScrollTo(targetId) {
        const targetElement = document.getElementById(targetId);
        if (targetElement) {
            const offsetTop = targetElement.offsetTop - 100; // Account for sticky header
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
            
            // Close menu after clicking
            if (isMenuOpen) {
                toggleMenu();
            }
        }
    }
    
    // Update active nav link based on scroll position
    function updateActiveNavLink() {
        const sections = [
            'global-filters',
            'metric-cards', 
            'charts-section',
            'campaigns-table',
            'daily-tracking',
            'pivot-advanced',
            'meta-report-insights',
            'insights-panel'
        ];
        
        const scrollPosition = window.scrollY + 150;
        
        sections.forEach(sectionId => {
            const section = document.getElementById(sectionId);
            const navLink = document.querySelector(`a[href="#${sectionId}"]`);
            
            if (section && navLink) {
                const sectionTop = section.offsetTop;
                const sectionBottom = sectionTop + section.offsetHeight;
                
                if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
                    // Remove active class from all links
                    navLinks.forEach(link => {
                        link.classList.remove('text-blue-600', 'bg-blue-50');
                        link.classList.add('text-gray-600');
                        const dot = link.querySelector('span:first-child');
                        if (dot) {
                            dot.classList.remove('bg-blue-600');
                            dot.classList.add('bg-gray-400');
                        }
                    });
                    
                    // Add active class to current link
                    navLink.classList.remove('text-gray-600');
                    navLink.classList.add('text-blue-600', 'bg-blue-50');
                    const dot = navLink.querySelector('span:first-child');
                    if (dot) {
                        dot.classList.remove('bg-gray-400');
                        dot.classList.add('bg-blue-600');
                    }
                }
            }
        });
    }
    
    // Event listeners
    if (navToggle) {
        navToggle.addEventListener('click', toggleMenu);
        console.log('Nav toggle listener added');
    }
    if (fabToggle) {
        fabToggle.addEventListener('click', toggleMenu);
        console.log('FAB toggle listener added');
    }
    
    // Handle nav link clicks
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            smoothScrollTo(targetId);
        });
    });
    
    // Update active link on scroll
    window.addEventListener('scroll', updateActiveNavLink);
    
    // Show/hide FAB based on scroll position (always show for now)
    window.addEventListener('scroll', function() {
        // FAB is always visible
        fabNav.classList.remove('hidden');
    });
    
    // Initialize - show FAB initially
    if (fabNav) {
        fabNav.classList.remove('hidden');
        console.log('FAB should be visible now');
    }
    
    // Keyboard navigation support
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && isMenuOpen) {
            toggleMenu();
        }
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
        if (isMenuOpen && !stickyNav.contains(e.target) && !fabNav.contains(e.target)) {
            toggleMenu();
        }
    });
});

/**
 * UNIFIED JAVASCRIPT - Reboot Reclaim Frontend
 * Handles all interactive functionality, WebSocket connections, and library integrations
 */

class RebootReclaimApp {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.theme = localStorage.getItem('theme') || 'dark';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeTheme();
        this.initializeMobileMenu();
        this.initializeAnimations();
        this.connectWebSocket();
        this.initializeLibraries();
    }

    setupEventListeners() {
        // Theme toggle
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }

        // Mobile menu toggle
        const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
        if (mobileMenuToggle) {
            mobileMenuToggle.addEventListener('click', () => this.toggleMobileMenu());
        }

        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => this.handleSmoothScroll(e));
        });

        // Close mobile menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.navbar')) {
                this.closeMobileMenu();
            }
        });

        // Handle window resize
        window.addEventListener('resize', () => this.handleResize());

        // Keyboard navigation
        document.addEventListener('keydown', (e) => this.handleKeyboardNavigation(e));
    }

    initializeTheme() {
        document.documentElement.setAttribute('data-theme', this.theme);
        const themeIcon = document.querySelector('#theme-toggle i');
        if (themeIcon) {
            themeIcon.className = this.theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }

    toggleTheme() {
        this.theme = this.theme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', this.theme);
        localStorage.setItem('theme', this.theme);

        const themeIcon = document.querySelector('#theme-toggle i');
        if (themeIcon) {
            themeIcon.className = this.theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }

        // Trigger theme change animation
        anime({
            targets: 'body',
            backgroundColor: this.theme === 'dark' ? '#0f1117' : '#ffffff',
            color: this.theme === 'dark' ? '#ffffff' : '#1f2937',
            duration: 300,
            easing: 'easeInOutQuad'
        });
    }

    initializeMobileMenu() {
        this.navLinks = document.getElementById('nav-links');
        this.mobileToggle = document.getElementById('mobile-menu-toggle');
    }

    toggleMobileMenu() {
        if (this.navLinks && this.mobileToggle) {
            const isActive = this.navLinks.classList.contains('active');
            if (isActive) {
                this.closeMobileMenu();
            } else {
                this.openMobileMenu();
            }
        }
    }

    openMobileMenu() {
        if (this.navLinks && this.mobileToggle) {
            this.navLinks.classList.add('active');
            this.mobileToggle.innerHTML = '<i class="fas fa-times"></i>';

            // Animate menu items
            anime({
                targets: '.nav-links a',
                translateX: [-20, 0],
                opacity: [0, 1],
                delay: anime.stagger(100),
                duration: 300,
                easing: 'easeOutQuad'
            });
        }
    }

    closeMobileMenu() {
        if (this.navLinks && this.mobileToggle) {
            this.navLinks.classList.remove('active');
            this.mobileToggle.innerHTML = '<i class="fas fa-bars"></i>';
        }
    }

    handleSmoothScroll(e) {
        const href = e.currentTarget.getAttribute('href');
        if (href.startsWith('#')) {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                const offsetTop = target.offsetTop - 100;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        }
    }

    handleResize() {
        if (window.innerWidth > 768) {
            this.closeMobileMenu();
        }
    }

    handleKeyboardNavigation(e) {
        // Escape key closes mobile menu
        if (e.key === 'Escape') {
            this.closeMobileMenu();
        }

        // Ctrl/Cmd + Shift + T toggles theme
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
            e.preventDefault();
            this.toggleTheme();
        }
    }

    connectWebSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;

            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = (event) => {
                this.isConnected = true;
                this.updateConnectionStatus('connected');
                console.log('WebSocket connected');
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            this.ws.onclose = (event) => {
                this.isConnected = false;
                this.updateConnectionStatus('disconnected');
                console.log('WebSocket disconnected');

                // Attempt to reconnect after 5 seconds
                setTimeout(() => this.connectWebSocket(), 5000);
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus('error');
            };
        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
            this.updateConnectionStatus('error');
        }
    }

    updateConnectionStatus(status) {
        const statusEl = document.getElementById('connection-status');
        if (!statusEl) return;

        const icon = statusEl.querySelector('i');
        const text = statusEl.querySelector('span');

        statusEl.className = `connection-status ${status}`;

        switch(status) {
            case 'connected':
                icon.className = 'fas fa-circle';
                icon.style.color = '#16a34a';
                text.textContent = 'Connected';
                break;
            case 'disconnected':
                icon.className = 'fas fa-circle';
                icon.style.color = '#ef4444';
                text.textContent = 'Disconnected';
                break;
            case 'error':
                icon.className = 'fas fa-exclamation-triangle';
                icon.style.color = '#f59e0b';
                text.textContent = 'Error';
                break;
        }
    }

    handleWebSocketMessage(data) {
        console.log('Received WebSocket message:', data);

        // Handle different types of real-time updates
        switch(data.type) {
            case 'device_update':
                this.handleDeviceUpdate(data);
                break;
            case 'progress_update':
                this.handleProgressUpdate(data);
                break;
            case 'blockchain_update':
                this.handleBlockchainUpdate(data);
                break;
            case 'notification':
                this.showNotification(data.title, data.message, data.level || 'info');
                break;
            case 'system_status':
                this.handleSystemStatus(data);
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    handleDeviceUpdate(data) {
        // Update device status in the UI
        if (window.updateDeviceStatus) {
            window.updateDeviceStatus(data.device_id, data.status);
        }

        // Trigger animations for status changes
        const deviceElement = document.querySelector(`[data-device-id="${data.device_id}"]`);
        if (deviceElement) {
            this.animateDeviceStatusChange(deviceElement, data.status);
        }
    }

    handleProgressUpdate(data) {
        if (window.updateProgress) {
            window.updateProgress(data.progress, data.message);
        }

        // Update progress bars
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');

        if (progressFill) {
            anime({
                targets: progressFill,
                width: `${data.progress}%`,
                duration: 500,
                easing: 'easeInOutQuad'
            });
        }

        if (progressText) {
            progressText.textContent = `${data.progress}% - ${data.message}`;
        }
    }

    handleBlockchainUpdate(data) {
        if (window.updateBlockchain) {
            window.updateBlockchain(data);
        }

        // Show notification for new blocks
        if (data.action === 'new_block') {
            this.showNotification(
                'New Certificate Added',
                `Certificate ${data.certificate_id} has been added to the blockchain`,
                'success'
            );
        }
    }

    handleSystemStatus(data) {
        // Update system statistics
        if (data.stats) {
            this.updateSystemStats(data.stats);
        }
    }

    animateDeviceStatusChange(element, newStatus) {
        const colors = {
            'ready': '#16a34a',
            'wiping': '#f59e0b',
            'completed': '#00f6ff',
            'error': '#ef4444'
        };

        anime({
            targets: element,
            backgroundColor: colors[newStatus] || '#6b7280',
            scale: [1, 1.05, 1],
            duration: 600,
            easing: 'easeInOutQuad'
        });
    }

    updateSystemStats(stats) {
        // Update stat cards with animation
        Object.keys(stats).forEach(key => {
            const element = document.getElementById(key);
            if (element) {
                anime({
                    targets: element,
                    innerHTML: [element.textContent, stats[key]],
                    duration: 1000,
                    easing: 'easeInOutQuad',
                    round: 1
                });
            }
        });
    }

    showNotification(title, message, type = 'info') {
        // Use SweetAlert2 for beautiful notifications
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: title,
                text: message,
                icon: type,
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 4000,
                timerProgressBar: true,
                customClass: {
                    popup: 'notification-popup'
                },
                showClass: {
                    popup: 'animate__animated animate__fadeInRight'
                },
                hideClass: {
                    popup: 'animate__animated animate__fadeOutRight'
                }
            });
        } else {
            // Fallback to browser notification
            this.showBrowserNotification(title, message);
        }
    }

    showBrowserNotification(title, message) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: message,
                icon: '/static/images/logo.png'
            });
        }
    }

    initializeAnimations() {
        // Initialize AOS (Animate On Scroll) if available
        if (typeof AOS !== 'undefined') {
            AOS.init({
                duration: 800,
                easing: 'ease-in-out',
                once: true,
                offset: 100
            });
        }

        // Add entrance animations to cards and elements
        const animatedElements = document.querySelectorAll('.card, .feature-card, .stat-item');
        animatedElements.forEach((element, index) => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(30px)';

            setTimeout(() => {
                anime({
                    targets: element,
                    opacity: 1,
                    translateY: 0,
                    duration: 600,
                    delay: index * 100,
                    easing: 'easeOutQuad'
                });
            }, 100);
        });
    }

    initializeLibraries() {
        // Initialize particles.js if on homepage
        if (document.getElementById('particles-js')) {
            this.initializeParticles();
        }

        // Initialize Three.js scenes where needed
        if (window.ThreeJSHandler) {
            window.ThreeJSHandler.init();
        }

        // Initialize Chart.js charts
        this.initializeCharts();

        // Initialize TypeIt for typing animations
        this.initializeTypeIt();
    }

    initializeParticles() {
        particlesJS("particles-js", {
            particles: {
                number: {
                    value: 80,
                    density: {
                        enable: true,
                        value_area: 800
                    }
                },
                color: {
                    value: "#00f6ff"
                },
                shape: {
                    type: "circle",
                    stroke: {
                        width: 0,
                        color: "#00f6ff"
                    }
                },
                opacity: {
                    value: 0.5,
                    random: true
                },
                size: {
                    value: 3,
                    random: true
                },
                line_linked: {
                    enable: true,
                    distance: 150,
                    color: "#00f6ff",
                    opacity: 0.4,
                    width: 1
                },
                move: {
                    enable: true,
                    speed: 2,
                    direction: "none",
                    random: true,
                    straight: false,
                    out_mode: "out",
                    bounce: false
                }
            },
            interactivity: {
                detect_on: "canvas",
                events: {
                    onhover: {
                        enable: true,
                        mode: "grab"
                    },
                    onclick: {
                        enable: true,
                        mode: "push"
                    },
                    resize: true
                },
                modes: {
                    grab: {
                        distance: 140,
                        line_linked: {
                            opacity: 1
                        }
                    },
                    push: {
                        particles_nb: 4
                    }
                }
            },
            retina_detect: true
        });
    }

    initializeCharts() {
        // Initialize Chart.js charts with consistent styling
        const charts = document.querySelectorAll('[data-chart]');
        charts.forEach(chartElement => {
            const chartType = chartElement.dataset.chart;
            const chartData = JSON.parse(chartElement.dataset.chartData || '{}');

            new Chart(chartElement, {
                type: chartType,
                data: chartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                color: '#ffffff'
                            }
                        }
                    },
                    scales: {
                        y: {
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            ticks: {
                                color: '#94a3b8'
                            }
                        },
                        x: {
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            ticks: {
                                color: '#94a3b8'
                            }
                        }
                    },
                    animation: {
                        duration: 1500,
                        easing: 'easeInOutQuart'
                    }
                }
            });
        });
    }

    initializeTypeIt() {
        // Initialize TypeIt for typing animations
        const typeElements = document.querySelectorAll('[data-typeit]');
        typeElements.forEach(element => {
            const options = JSON.parse(element.dataset.typeit || '{}');
            new TypeIt(element, {
                strings: options.strings || [''],
                speed: options.speed || 100,
                loop: options.loop || false,
                ...options
            });
        });
    }

    // Utility methods
    showLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.add('active');
        }
    }

    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.remove('active');
        }
    }

    // Public API methods for other scripts to use
    sendWebSocketMessage(data) {
        if (this.ws && this.isConnected) {
            this.ws.send(JSON.stringify(data));
        }
    }

    updateProgress(progress, message) {
        this.handleProgressUpdate({ progress, message });
    }

    showSuccessNotification(title, message) {
        this.showNotification(title, message, 'success');
    }

    showErrorNotification(title, message) {
        this.showNotification(title, message, 'error');
    }

    showWarningNotification(title, message) {
        this.showNotification(title, message, 'warning');
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.RebootReclaimApp = new RebootReclaimApp();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RebootReclaimApp;
}

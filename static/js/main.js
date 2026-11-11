document.addEventListener("DOMContentLoaded", function () {

    const sidebar = document.getElementById("sidebar");
    const menuButton = document.getElementById("mobileMenuBtn");
    const overlay = document.getElementById("sidebarOverlay");

    // Open / close sidebar
    if (menuButton && sidebar && overlay) {

        menuButton.addEventListener("click", function () {
            sidebar.classList.toggle("show");
            overlay.classList.toggle("show");
        });

        // Close sidebar when overlay is clicked
        overlay.addEventListener("click", function () {
            sidebar.classList.remove("show");
            overlay.classList.remove("show");
        });

        // Close sidebar after clicking a navigation link on mobile
        const navLinks = sidebar.querySelectorAll(".nav-link, .nav-item");

        navLinks.forEach(function (link) {
            link.addEventListener("click", function () {
                if (window.innerWidth <= 992) {
                    sidebar.classList.remove("show");
                    overlay.classList.remove("show");
                }
            });
        });

    }

    // Highlight current navigation item
    const currentPath = window.location.pathname;

    const navigationLinks =
        document.querySelectorAll(".sidebar .nav-link, .sidebar .nav-item");

    navigationLinks.forEach(function (link) {
        const href = link.getAttribute("href");

        if (
            href &&
            href !== "#" &&
            currentPath === new URL(
                href,
                window.location.origin
            ).pathname
        ) {
            link.classList.add("active");
        }
    });

    // Automatically close sidebar if screen becomes large
    window.addEventListener("resize", function () {
        if (window.innerWidth > 992) {
            if (sidebar) {
                sidebar.classList.remove("show");
            }
            if (overlay) {
                overlay.classList.remove("show");
            }
        }
    });

    // Optional Auto-dismiss flash alert messages after 5 seconds
    const flashAlerts = document.querySelectorAll(".flash-container .alert, .flash-stack .alert");
    flashAlerts.forEach(function (alert) {
        setTimeout(function () {
            try {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                if (bsAlert) {
                    bsAlert.close();
                }
            } catch (e) {
                // Ignore if bootstrap alert instance not available
            }
        }, 5000);
    });

});
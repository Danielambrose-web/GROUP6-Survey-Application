// Simple mobile navigation toggle
document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.getElementById('nav-toggle');
    const mobileDropdown = document.getElementById('mobile-dropdown');

    if (navToggle && mobileDropdown) {
        navToggle.addEventListener('click', function() {
            mobileDropdown.classList.toggle('show');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            if (!navToggle.contains(event.target) && !mobileDropdown.contains(event.target)) {
                mobileDropdown.classList.remove('show');
            }
        });

        // Close dropdown when clicking on a link
        const dropdownLinks = mobileDropdown.querySelectorAll('.dropdown-link');
        dropdownLinks.forEach(link => {
            link.addEventListener('click', function() {
                mobileDropdown.classList.remove('show');
            });
        });
    }
});

// Global image error handler — prevents infinite reload loops.
// If a profile/provider image fails to load, swap to the SVG fallback once.
// If even the fallback fails, replace with an inline SVG data URI so nothing loops.
(function () {
    const AVATAR_FALLBACK   = '/static/images/default-avatar.svg';
    const PROVIDER_FALLBACK = '/static/images/default-provider.svg';

    const INLINE_AVATAR = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' fill='%23e2e8f0' rx='50'/%3E%3Ccircle cx='50' cy='38' r='18' fill='%2394a3b8'/%3E%3Cellipse cx='50' cy='82' rx='28' ry='20' fill='%2394a3b8'/%3E%3C/svg%3E";
    const INLINE_PROVIDER = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' fill='%23dbeafe' rx='50'/%3E%3Ccircle cx='50' cy='36' r='17' fill='%2360a5fa'/%3E%3Cellipse cx='50' cy='80' rx='26' ry='18' fill='%2360a5fa'/%3E%3C/svg%3E";

    function handleImageError(img) {
        // Already tried fallback — use inline data URI, never fires onerror again
        if (img.dataset.fallbackUsed) {
            const isProvider = img.dataset.fallbackType === 'provider';
            img.src = isProvider ? INLINE_PROVIDER : INLINE_AVATAR;
            img.onerror = null;
            return;
        }

        img.dataset.fallbackUsed = '1';

        const src = img.getAttribute('src') || '';
        const isProvider = src.includes('provider') ||
                           img.dataset.fallbackType === 'provider' ||
                           img.classList.contains('provider-img');

        img.dataset.fallbackType = isProvider ? 'provider' : 'avatar';

        const fallback = isProvider ? PROVIDER_FALLBACK : AVATAR_FALLBACK;

        // Don't loop if we're already trying to load the fallback
        if (src === fallback) {
            img.src = isProvider ? INLINE_PROVIDER : INLINE_AVATAR;
            img.onerror = null;
            return;
        }

        img.src = fallback;
    }

    // Attach to all current images
    function attachHandlers() {
        document.querySelectorAll('img').forEach(function (img) {
            if (img.dataset.errorHandled) return;
            img.dataset.errorHandled = '1';
            img.addEventListener('error', function () {
                handleImageError(img);
            });
        });
    }

    // Run on DOM ready and observe future images added dynamically
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', attachHandlers);
    } else {
        attachHandlers();
    }

    const observer = new MutationObserver(attachHandlers);
    document.addEventListener('DOMContentLoaded', function () {
        observer.observe(document.body, { childList: true, subtree: true });
    });
}());

document.addEventListener('DOMContentLoaded', function () {

    // Auto-dismiss toasts
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(function (toastEl) {
        const toast = new bootstrap.Toast(toastEl, { delay: 4500 });
        toast.show();
    });

    // Notification badge polling
    const badge = document.getElementById('notif-badge');
    if (badge) {
        function fetchUnreadCount() {
            fetch('/notifications/unread-count/')
                .then(r => r.json())
                .then(data => {
                    if (data.count > 0) {
                        badge.textContent = data.count;
                        badge.classList.remove('d-none');
                    } else {
                        badge.classList.add('d-none');
                    }
                })
                .catch(() => {});
        }

        fetchUnreadCount();
        setInterval(fetchUnreadCount, 30000);
    }

    // Confirm delete/cancel actions on forms with data-confirm
    document.querySelectorAll('form[data-confirm]').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            const msg = form.getAttribute('data-confirm');
            if (!confirm(msg)) {
                e.preventDefault();
            }
        });
    });

    // Highlight active nav link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.navbar .nav-link').forEach(function (link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Animate stat numbers on dashboard
    document.querySelectorAll('.stat-number').forEach(function (el) {
        const target = parseInt(el.textContent, 10);
        if (isNaN(target)) return;
        let current = 0;
        const step = Math.ceil(target / 30);
        const timer = setInterval(function () {
            current = Math.min(current + step, target);
            el.textContent = current;
            if (current >= target) clearInterval(timer);
        }, 30);
    });

    // Date input: prevent past dates on booking form
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(function (input) {
        if (!input.min) {
            const today = new Date().toISOString().split('T')[0];
            input.min = today;
        }
    });

    // Time validation: end time must be after start time
    const startTime = document.querySelector('input[name="start_time"]');
    const endTime = document.querySelector('input[name="end_time"]');
    if (startTime && endTime) {
        startTime.addEventListener('change', function () {
            endTime.min = startTime.value;
            if (endTime.value && endTime.value <= startTime.value) {
                endTime.value = '';
            }
        });
    }

    // Tooltip initialization
    const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipEls.forEach(function (el) {
        new bootstrap.Tooltip(el);
    });

    // Smooth fade-in for cards
    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.card').forEach(function (card) {
        card.style.opacity = '0';
        card.style.transform = 'translateY(10px)';
        card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        observer.observe(card);
    });

});

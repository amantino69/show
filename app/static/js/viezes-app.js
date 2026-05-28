/**
 * Viezes — detecção de dispositivo, menu mobile e UX touch
 */
(function () {
    'use strict';

    const BP_MOBILE = 768;
    const BP_DESKTOP = 992;

    function detectDevice() {
        const w = window.innerWidth;
        const ua = navigator.userAgent || '';
        const coarse = window.matchMedia('(pointer: coarse)').matches;
        const touch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

        let type = 'desktop';
        if (w < BP_MOBILE) type = 'mobile';
        else if (w < BP_DESKTOP) type = 'tablet';

        return { type, width: w, touch, coarse, ua };
    }

    function applyDeviceClasses() {
        const body = document.body;
        if (!body) return;
        const { type, touch, coarse } = detectDevice();

        body.classList.remove('device-mobile', 'device-tablet', 'device-desktop');
        body.classList.add('device-' + type);

        body.classList.toggle('has-touch', touch);
        body.classList.toggle('has-coarse-pointer', coarse);
    }

    function initMobileMenu() {
        const toggle = document.getElementById('mobileMenuToggle');
        const sidebar = document.getElementById('mobileSidebar');
        const overlay = document.getElementById('mobileOverlay');
        const closeBtn = document.getElementById('mobileSidebarClose');

        if (!toggle || !sidebar || !overlay) return;

        function openMenu() {
            sidebar.classList.add('open');
            overlay.classList.add('show');
            document.body.classList.add('vz-menu-open');
            toggle.setAttribute('aria-expanded', 'true');
        }

        function closeMenu() {
            sidebar.classList.remove('open');
            overlay.classList.remove('show');
            document.body.classList.remove('vz-menu-open');
            toggle.setAttribute('aria-expanded', 'false');
        }

        function toggleMenu() {
            if (sidebar.classList.contains('open')) closeMenu();
            else openMenu();
        }

        toggle.addEventListener('click', function (e) {
            e.preventDefault();
            toggleMenu();
        });

        if (closeBtn) {
            closeBtn.addEventListener('click', function (e) {
                e.preventDefault();
                closeMenu();
            });
        }

        overlay.addEventListener('click', closeMenu);

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') closeMenu();
        });

        sidebar.querySelectorAll('.nav-link').forEach(function (link) {
            link.addEventListener('click', function () {
                setTimeout(closeMenu, 120);
            });
        });

        document.querySelectorAll('[data-vz-open-menu]').forEach(function (el) {
            el.addEventListener('click', function (e) {
                e.preventDefault();
                openMenu();
            });
        });

        window.addEventListener('resize', function () {
            if (window.innerWidth >= BP_DESKTOP) closeMenu();
        });
    }

    function markBottomNavActive() {
        const path = window.location.pathname;
        document.querySelectorAll('.mobile-bottom-nav a[data-nav]').forEach(function (a) {
            const match = a.getAttribute('data-nav-match');
            if (!match) return;
            const patterns = match.split('|');
            const active = patterns.some(function (p) {
                if (p === '/') return path === '/' || path === '';
                if (p.endsWith('*')) return path.startsWith(p.slice(0, -1));
                return path === p || path.startsWith(p + '/');
            });
            a.classList.toggle('active', active);
        });
    }

    function enhanceTables() {
        document.querySelectorAll('.table').forEach(function (table) {
            if (table.closest('.vz-table-wrap')) return;
            const wrap = document.createElement('div');
            wrap.className = 'vz-table-wrap';
            table.parentNode.insertBefore(wrap, table);
            wrap.appendChild(table);
        });
    }

    function init() {
        applyDeviceClasses();
        initMobileMenu();
        markBottomNavActive();
        enhanceTables();

        var resizeTimer;
        window.addEventListener('resize', function () {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(applyDeviceClasses, 150);
        });

        window.addEventListener('orientationchange', function () {
            setTimeout(applyDeviceClasses, 200);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

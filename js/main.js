/* ===================================
   PayForge — Main JS (Redesigned)
   =================================== */

(function () {
    'use strict';

    // ============ COUNTRY DATA ============
    var TELEGRAM_BOT_URL = 'https://t.me/PayForgeBot';

    var countries = [
        { name: 'Pakistan', flag: '🇵🇰', region: 'Asia' },
        { name: 'Bangladesh', flag: '🇧🇩', region: 'Asia' },
        { name: 'Tunisia', flag: '🇹🇳', region: 'Africa' },
        { name: 'Ethiopia', flag: '🇪🇹', region: 'Africa' },
        { name: 'Egypt', flag: '🇪🇬', region: 'Africa' },
        { name: 'Bhutan', flag: '🇧🇹', region: 'Asia' },
        { name: 'Costa Rica', flag: '🇨🇷', region: 'Latin America' },
        { name: 'Argentina', flag: '🇦🇷', region: 'Latin America' },
        { name: 'Ecuador', flag: '🇪🇨', region: 'Latin America' },
        { name: 'Dominican Republic', flag: '🇩🇴', region: 'Latin America' },
        { name: 'Honduras', flag: '🇭🇳', region: 'Latin America' },
        { name: 'El Salvador', flag: '🇸🇻', region: 'Latin America' },
        { name: 'Panama', flag: '🇵🇦', region: 'Latin America' },
        { name: 'Paraguay', flag: '🇵🇾', region: 'Latin America' },
        { name: 'Uruguay', flag: '🇺🇾', region: 'Latin America' },
        { name: 'Jamaica', flag: '🇯🇲', region: 'Latin America' },
        { name: 'Nepal', flag: '🇳🇵', region: 'Asia' },
        { name: 'Guatemala', flag: '🇬🇹', region: 'Latin America' },
        { name: 'Cambodia', flag: '🇰🇭', region: 'Asia' },
        { name: 'India', flag: '🇮🇳', region: 'Asia' },
        { name: 'Algeria', flag: '🇩🇿', region: 'Africa' },
        { name: 'Senegal', flag: '🇸🇳', region: 'Africa' },
        { name: 'Mali', flag: '🇲🇱', region: 'Africa' },
        { name: 'Guinea', flag: '🇬🇳', region: 'Africa' },
        { name: 'Brunei', flag: '🇧🇳', region: 'Asia' },
        { name: 'Papua New Guinea', flag: '🇵🇬', region: 'Asia' },
        { name: 'Kenya', flag: '🇰🇪', region: 'Africa' },
        { name: 'Sri Lanka', flag: '🇱🇰', region: 'Asia' },
        { name: 'Bahrain', flag: '🇧🇭', region: 'Asia' },
        { name: 'Nicaragua', flag: '🇳🇮', region: 'Latin America' },
        { name: 'Laos', flag: '🇱🇦', region: 'Asia' },
        { name: 'Myanmar', flag: '🇲🇲', region: 'Asia' }
    ];

    // ============ RENDER CUSTOM DROPDOWN ============
    var selectBox = document.getElementById('countrySelect');
    var selectValue = document.getElementById('countrySelectValue');
    var optionsContainer = document.getElementById('countryOptions');
    var partnerBtn = document.getElementById('partnerBtn');

    if (selectBox && optionsContainer) {
        // Generate options
        countries.forEach(function (c) {
            var opt = document.createElement('div');
            opt.className = 'custom-select__option';
            opt.innerHTML = '<span class="custom-select__option-flag">' + c.flag + '</span> <span>' + c.name + '</span>';

            opt.addEventListener('click', function () {
                selectValue.innerHTML = '<span class="custom-select__option-flag" style="margin-right:8px;">' + c.flag + '</span><span>' + c.name + '</span>';
                optionsContainer.classList.remove('custom-select__options--open');
                selectBox.classList.remove('custom-select--active');

                // Show and configure TG button
                partnerBtn.style.display = 'inline-flex';
                partnerBtn.href = TELEGRAM_BOT_URL + '?start=' + encodeURIComponent(c.name);
            });

            optionsContainer.appendChild(opt);
        });

        // Toggle dropdown
        selectBox.addEventListener('click', function () {
            var isOpen = optionsContainer.classList.contains('custom-select__options--open');
            if (isOpen) {
                optionsContainer.classList.remove('custom-select__options--open');
                selectBox.classList.remove('custom-select--active');
            } else {
                optionsContainer.classList.add('custom-select__options--open');
                selectBox.classList.add('custom-select--active');
            }
        });

        // Close on outside click
        document.addEventListener('click', function (e) {
            if (!selectBox.contains(e.target) && !optionsContainer.contains(e.target)) {
                optionsContainer.classList.remove('custom-select__options--open');
                selectBox.classList.remove('custom-select--active');
            }
        });
    }

    // ============ HERO & CTA BUTTON SCROLL ============
    var partnerLinks = document.querySelectorAll('a[href="#partners"]');
    partnerLinks.forEach(function (link) {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            var target = document.getElementById('partners');
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'center' });
                // Optional: briefly highlight the selector box
                setTimeout(function () {
                    selectBox.style.borderColor = 'var(--deep-red)';
                    setTimeout(function () {
                        selectBox.style.borderColor = '';
                    }, 600);
                }, 800);
            }
        });
    });

    // ============ MOBILE NAV ============
    var navToggle = document.getElementById('navToggle');
    var navLinks = document.getElementById('navLinks');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function () {
            navToggle.classList.toggle('nav__toggle--active');
            navLinks.classList.toggle('nav__links--open');
        });

        navLinks.querySelectorAll('.nav__link').forEach(function (link) {
            link.addEventListener('click', function () {
                navToggle.classList.remove('nav__toggle--active');
                navLinks.classList.remove('nav__links--open');
            });
        });
    }

    // ============ SCROLL REVEAL ============
    var reveals = document.querySelectorAll('.reveal');

    if (reveals.length > 0) {
        var observer = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('reveal--visible');
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.1, rootMargin: '0px 0px -30px 0px' }
        );

        reveals.forEach(function (el) { observer.observe(el); });
    }

    // ============ NAV SHADOW ON SCROLL + BACKGROUND TOGGLE ============
    var nav = document.getElementById('nav');
    var heroSection = document.getElementById('hero');

    window.addEventListener('scroll', function () {
        var heroBottom = heroSection ? heroSection.offsetHeight - 80 : 200;

        if (window.scrollY > 10) {
            nav.style.boxShadow = '0 1px 12px rgba(43,45,51,0.06)';
        } else {
            nav.style.boxShadow = 'none';
        }

        // Toggle solid background when past hero section
        if (window.scrollY > heroBottom) {
            nav.classList.add('nav--scrolled');
        } else {
            nav.classList.remove('nav--scrolled');
        }
    }, { passive: true });

})();

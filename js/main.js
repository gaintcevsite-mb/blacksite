/* ===================================
   PayForge — Main JS (Redesigned)
   =================================== */

(function () {
    'use strict';

    // ============ COUNTRY DATA ============
    var TELEGRAM_BOT_URL = 'https://t.me/PayForge_Bot';

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
                var safeName = c.name.replace(/\s+/g, '_');
                partnerBtn.href = TELEGRAM_BOT_URL + '?start=join_' + encodeURIComponent(safeName);
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

    // ============ LANGUAGE SWITCHER ============
    var langBtn = document.getElementById('langBtn');
    var langMenu = document.getElementById('langMenu');
    if (langBtn && langMenu) {
        langBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            langMenu.classList.toggle('lang-switch__menu--open');
        });
        document.addEventListener('click', function () {
            langMenu.classList.remove('lang-switch__menu--open');
        });
    }

    // ============ GEO IP AUTO-SELECT & REDIRECT ============
    // Only fetch if we don't have it saved, or perform actions if we do.
    async function initGeoIp() {
        let geoData = null;
        const storedGeo = sessionStorage.getItem('geo_data');

        if (storedGeo) {
            try {
                geoData = JSON.parse(storedGeo);
            } catch (e) { }
        }

        if (!geoData) {
            try {
                const res = await fetch('https://get.geojs.io/v1/ip/geo.json');
                if (res.ok) {
                    geoData = await res.json();
                    sessionStorage.setItem('geo_data', JSON.stringify(geoData));
                }
            } catch (error) {
                console.error('GeoIP fetch error:', error);
            }
        }

        if (geoData && geoData.country_code) {
            const countryCode = geoData.country_code; // e.g. "ES", "AR", "PA"
            const countryNameStr = geoData.country; // e.g. "Panama"

            // 1. Language Auto-Redirect
            // If user is from a Spanish-speaking country and on index.html, redirect once.
            const isIndex = window.location.pathname.endsWith('index.html') || window.location.pathname === '/' || window.location.pathname.indexOf('.html') === -1;
            const redirected = sessionStorage.getItem('lang_redirected');

            const latamESCodes = ['AR', 'BO', 'CL', 'CO', 'CR', 'CU', 'DO', 'EC', 'SV', 'GQ', 'GT', 'HN', 'MX', 'NI', 'PA', 'PY', 'PE', 'PR', 'ES', 'UY', 'VE'];

            if (isIndex && !redirected && latamESCodes.includes(countryCode)) {
                sessionStorage.setItem('lang_redirected', 'true');
                window.location.href = 'es.html';
                return; // Stop execution as we are leaving the page
            } else if (!redirected) {
                // Mark as checked to prevent future loops if they manually switch
                sessionStorage.setItem('lang_redirected', 'true');
            }

            // 2. Auto-Select "Become a Partner" dropdown
            if (selectBox && optionsContainer) {
                // Find matching country in our array
                const matchedCountry = countries.find(c => c.name.toLowerCase() === countryNameStr.toLowerCase());

                if (matchedCountry) {
                    // Update UI safely
                    if (selectValue) {
                        selectValue.innerHTML = '<span class="custom-select__option-flag" style="margin-right:8px;">' + matchedCountry.flag + '</span><span>' + matchedCountry.name + '</span>';
                    }
                    if (partnerBtn) {
                        partnerBtn.style.display = 'inline-flex';
                        var safeName = matchedCountry.name.replace(/\s+/g, '_');
                        partnerBtn.href = TELEGRAM_BOT_URL + '?start=join_' + encodeURIComponent(safeName);
                    }
                    console.log('GeoIP Auto-selected:', matchedCountry.name);
                }
            }
        }
    }

    // Run GeoIP logic
    initGeoIp();

})();

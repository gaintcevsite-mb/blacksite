/* ===================================
   PayForge — Main JS (iGaming Redesign)
   =================================== */

(function () {
    'use strict';

    // ============ COUNTRY DATA ============
    var TELEGRAM_BOT_URL = 'https://t.me/payforgelead_bot';

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

    // ============ DYNAMIC CONDITIONS ============
    // Use inline data from conditions-data.js (works with file:// protocol)
    var conditionsData = (typeof CONDITIONS_DATA !== 'undefined') ? CONDITIONS_DATA : {};

    // Also try to fetch for web server deployments
    if (Object.keys(conditionsData).length === 0) {
        fetch('conditions.json')
            .then(function(res) { return res.json(); })
            .then(function(data) {
                conditionsData = data.countries || {};
            })
            .catch(function(err) {
                console.warn('conditions.json fetch failed, using inline data', err);
            });
    }

    function renderConditions(countryFullName) {
        var data = conditionsData[countryFullName];
        if (!data) return;

        var displayBox = document.getElementById('conditionsDisplay');
        if (!displayBox) {
            displayBox = document.createElement('div');
            displayBox.id = 'conditionsDisplay';
            var pbox = document.querySelector('.partner-box');
            if (pbox && partnerBtn) {
                pbox.insertBefore(displayBox, partnerBtn);
            }
        }

        var traffic = data.trafficPercentage || 50;
        var earnings = data.earningsValue || 'Variable';
        var conds = data.conditions || [];

        var listHtml = '<ul class="cond-list">';
        conds.forEach(function(c) {
            listHtml += '<li>' + c + '</li>';
        });
        listHtml += '</ul>';

        // Calculate earnings progress
        var eProg = 50;
        if (earnings.indexOf('500') > -1) eProg = 95;
        else if (earnings.indexOf('150') > -1) eProg = 80;
        else if (earnings.indexOf('100') > -1) eProg = 70;
        else if (earnings.indexOf('75') > -1) eProg = 60;
        else if (earnings.indexOf('50') > -1) eProg = 45;
        else if (earnings.indexOf('30') > -1) eProg = 30;
        else if (earnings.indexOf('5%') > -1) eProg = 85;
        else if (earnings.indexOf('4%') > -1) eProg = 90;

        displayBox.innerHTML =
            '<div class="cond-header"><span>' + countryFullName + '</span></div>' +
            '<div class="cond-stats">' +
            '  <div class="cond-stat">' +
            '    <div class="cond-stat-label">Traffic Volume</div>' +
            '    <div class="cond-stat-value">' + traffic + '%</div>' +
            '    <div class="progress-bar-bg"><div class="progress-bar-fill progress-bar-fill--traffic" id="trafficFill"></div></div>' +
            '  </div>' +
            '  <div class="cond-stat">' +
            '    <div class="cond-stat-label">Potential Earnings</div>' +
            '    <div class="cond-stat-value">' + earnings + '</div>' +
            '    <div class="progress-bar-bg"><div class="progress-bar-fill progress-bar-fill--earnings" id="earningsFill"></div></div>' +
            '  </div>' +
            '</div>' +
            listHtml;

        displayBox.style.display = 'block';

        // Animate progress bars after a short delay
        setTimeout(function() {
            var tFill = document.getElementById('trafficFill');
            var eFill = document.getElementById('earningsFill');
            if (tFill) tFill.style.width = traffic + '%';
            if (eFill) eFill.style.width = eProg + '%';
        }, 100);
    }

    // ============ DROPDOWN SETUP ============
    if (selectBox && optionsContainer) {
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

                // Show conditions for this country
                var cKey = Object.keys(conditionsData).find(function(k) {
                    return k.indexOf(c.name) > -1;
                });
                if (cKey) renderConditions(cKey);
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

    
    // ============ FLOAT CONTACT VISIBILITY ============
    document.addEventListener('DOMContentLoaded', function() {
        var floatContact = document.querySelector('.float-contact');
        if (floatContact) {
            window.addEventListener('scroll', function () {
                if (window.scrollY > 200) {
                    floatContact.classList.add('float-contact--visible');
                } else {
                    floatContact.classList.remove('float-contact--visible');
                }
            }, { passive: true });
        }
    });

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
            nav.style.boxShadow = '0 1px 12px rgba(0,0,0,0.3)';
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
            const countryCode = geoData.country_code;
            const countryNameStr = geoData.country;

            // 1. Language Auto-Redirect
            const isIndex = window.location.pathname.endsWith('index.html') || window.location.pathname === '/' || window.location.pathname.indexOf('.html') === -1;
            const redirected = sessionStorage.getItem('lang_redirected');

            const latamESCodes = ['AR', 'BO', 'CL', 'CO', 'CR', 'CU', 'DO', 'EC', 'SV', 'GQ', 'GT', 'HN', 'MX', 'NI', 'PA', 'PY', 'PE', 'PR', 'ES', 'UY', 'VE'];

            if (isIndex && !redirected && latamESCodes.includes(countryCode)) {
                sessionStorage.setItem('lang_redirected', 'true');
                window.location.href = 'es.html';
                return;
            } else if (!redirected) {
                sessionStorage.setItem('lang_redirected', 'true');
            }

            // 2. Auto-Select "Become a Partner" dropdown
            if (selectBox && optionsContainer) {
                const matchedCountry = countries.find(c => c.name.toLowerCase() === countryNameStr.toLowerCase());

                if (matchedCountry) {
                    if (selectValue) {
                        selectValue.innerHTML = '<span class="custom-select__option-flag" style="margin-right:8px;">' + matchedCountry.flag + '</span><span>' + matchedCountry.name + '</span>';
                    }
                    if (partnerBtn) {
                        partnerBtn.style.display = 'inline-flex';
                        var safeName = matchedCountry.name.replace(/\s+/g, '_');
                        partnerBtn.href = TELEGRAM_BOT_URL + '?start=join_' + encodeURIComponent(safeName);
                    }
                    console.log('GeoIP Auto-selected:', matchedCountry.name);

                    // Auto-show conditions for detected country
                    var geoCKey = Object.keys(conditionsData).find(function(k) {
                        return k.indexOf(matchedCountry.name) > -1;
                    });
                    if (geoCKey) {
                        renderConditions(geoCKey);
                    }
                }
            }
        }
    }

    // Run GeoIP logic
    initGeoIp();

})();

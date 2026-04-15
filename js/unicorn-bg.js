/* ===================================
   Unicorn Studio — Background Init + Watermark Killer
   =================================== */
(function () {
    'use strict';

    // Load SDK
    var script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/gh/hiunicornstudio/unicornstudio.js@v2.1.9/dist/unicornStudio.umd.js';
    script.onload = function () {
        UnicornStudio.init();
    };
    (document.head || document.body).appendChild(script);

    // Watermark killer
    var kill = function () {
        document.querySelectorAll(
            'a[href*="unicorn"], a[href*="made-with"], [class*="badge"], [id*="badge"], [class*="watermark"], [id*="watermark"], canvas ~ a, div[data-us-project] > a, .us-badge, #us-badge'
        ).forEach(function (el) {
            el.style.setProperty('display', 'none', 'important');
            el.remove();
        });

        var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
        var node;
        while (node = walker.nextNode()) {
            if (node.nodeValue && node.nodeValue.toLowerCase().indexOf('unicorn.studio') > -1) {
                var el = node.parentElement;
                if (el && el.tagName !== 'SCRIPT' && el.tagName !== 'STYLE') {
                    var container = el.closest('a') || el.closest('div');
                    if (container && !container.hasAttribute('data-us-project') && !container.classList.contains('us-bg')) {
                        container.style.setProperty('display', 'none', 'important');
                        container.remove();
                    }
                }
            }
        }

        var usDiv = document.querySelector('div[data-us-project]');
        if (usDiv && usDiv.shadowRoot) {
            usDiv.shadowRoot.querySelectorAll('a, [class*="badge"], div:not([data-us-project])').forEach(function (child) {
                child.style.setProperty('display', 'none', 'important');
                child.remove();
            });
        }
    };

    new MutationObserver(kill).observe(document.documentElement, { childList: true, subtree: true });
    setInterval(kill, 200);
})();

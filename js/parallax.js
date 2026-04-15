/* ===================================
   PayForge — Parallax iGaming Figures
   Mouse-tracking parallax for desktop
   =================================== */

(function () {
    'use strict';

    if (window.innerWidth <= 768) return;

    var items = document.querySelectorAll('.parallax-item');
    if (!items.length) return;

    document.addEventListener('mousemove', function (e) {
        var cx = window.innerWidth / 2;
        var cy = window.innerHeight / 2;
        var dx = (e.clientX - cx) / cx;
        var dy = (e.clientY - cy) / cy;

        items.forEach(function (item, i) {
            var speed = parseFloat(item.getAttribute('data-speed')) || (10 + i * 5);
            var xOff = dx * speed;
            var yOff = dy * speed;
            item.style.transform = 'translate(' + xOff + 'px, ' + yOff + 'px)';
        });
    });
})();

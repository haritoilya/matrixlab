/* matrixlab.pro — замена скриптов конструктора Т-Банка.
   Без зависимостей. Подключается на всех страницах: <script src="/assets/js/site.js" defer> */
(function () {
  'use strict';

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* 1. Меню-бургер (мобильная версия) */
  $$('.js-wrapper').forEach(function (wrap) {
    var burger = $('.js-burger', wrap);
    var menu = $('.js-menu', wrap);
    if (!burger || !menu) return;
    burger.setAttribute('role', 'button');
    burger.setAttribute('tabindex', '0');
    burger.setAttribute('aria-label', 'Меню');
    burger.setAttribute('aria-expanded', 'false');

    var header = burger.closest('.s-header-type-2');
    function setOpen(open) {
      if (header) header.classList.toggle('js-active', open);
      burger.classList.toggle('js-burger_open', open);
      menu.classList.toggle('js-menu_open', open);
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      document.body.style.overflow = open ? 'hidden' : '';
    }
    burger.addEventListener('click', function () {
      setOpen(!burger.classList.contains('js-burger_open'));
    });
    burger.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); burger.click(); }
    });
    $$('a', menu).forEach(function (a) {
      a.addEventListener('click', function () { setOpen(false); });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') setOpen(false);
    });
  });

  /* 2. FAQ-аккордеон */
  $$('.s-faq-type-3__question').forEach(function (q) {
    var ask = $('.s-faq-type-3__ask', q);
    var answer = $('.s-faq-type-3__answer', q);
    if (!ask || !answer) return;
    ask.setAttribute('role', 'button');
    ask.setAttribute('tabindex', '0');
    ask.setAttribute('aria-expanded', 'false');

    function sync() {
      var open = q.classList.contains('s-faq-type-3__question_open');
      answer.style.height = open ? answer.scrollHeight + 'px' : '0px';
      ask.setAttribute('aria-expanded', open ? 'true' : 'false');
    }
    function toggle() {
      q.classList.toggle('s-faq-type-3__question_open');
      sync();
    }
    ask.addEventListener('click', toggle);
    ask.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); }
    });
    window.addEventListener('resize', function () {
      if (q.classList.contains('s-faq-type-3__question_open')) sync();
    });
  });

  /* 3. Слайдер товаров на главной (стрелки, точки, свайп) */
  $$('.s-product-services-type-4__slider').forEach(function (root) {
    var list = $('.js-list', root);
    var slides = $$('.js-slide', root);
    var prev = $('.js-arrow_previous', root);
    var next = $('.js-arrow_next', root);
    var dots = $('.js-dots', root);
    if (!list || slides.length < 2) {
      [prev, next].forEach(function (el) { if (el) el.style.display = 'none'; });
      return;
    }
    var index = 0;
    list.style.transition = 'transform .4s ease';

    function render() {
      list.style.transform = 'translateX(' + (-index * 100) + '%)';
      if (dots) {
        $$('.site-dot', dots).forEach(function (d, i) {
          d.classList.toggle('site-dot_active', i === index);
          d.setAttribute('aria-current', i === index ? 'true' : 'false');
        });
      }
    }
    function go(i) {
      index = (i + slides.length) % slides.length;
      render();
    }
    if (dots) {
      dots.innerHTML = '';
      slides.forEach(function (_, i) {
        var li = document.createElement('li');
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'site-dot';
        b.setAttribute('aria-label', 'Слайд ' + (i + 1));
        b.addEventListener('click', function () { go(i); });
        li.appendChild(b);
        dots.appendChild(li);
      });
    }
    if (prev) prev.addEventListener('click', function () { go(index - 1); });
    if (next) next.addEventListener('click', function () { go(index + 1); });

    var startX = null;
    root.addEventListener('touchstart', function (e) { startX = e.touches[0].clientX; }, { passive: true });
    root.addEventListener('touchend', function (e) {
      if (startX === null) return;
      var dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 40) go(index + (dx < 0 ? 1 : -1));
      startX = null;
    });
    render();
  });

  /* 4. Увеличение фото товара */
  var box = null;
  function closeBox() { if (box) { box.remove(); box = null; document.body.style.overflow = ''; } }
  $$('.sb-image-zoom[data-popup-id]').forEach(function (el) {
    el.addEventListener('click', function () {
      var img = $('img', el);
      if (!img) return;
      closeBox();
      box = document.createElement('div');
      box.className = 'site-lightbox';
      box.setAttribute('role', 'dialog');
      box.setAttribute('aria-modal', 'true');
      var big = document.createElement('img');
      big.src = img.currentSrc || img.src;
      big.alt = img.alt || '';
      var x = document.createElement('button');
      x.type = 'button';
      x.className = 'site-lightbox__close';
      x.setAttribute('aria-label', 'Закрыть');
      x.textContent = '×';
      box.appendChild(big);
      box.appendChild(x);
      box.addEventListener('click', closeBox);
      document.body.appendChild(box);
      document.body.style.overflow = 'hidden';
    });
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeBox(); });

  /* 5. Слайдер «до/после» на странице «О продукте» */
  $$('.s-gallery-compare-type-1__panel').forEach(function (panel) {
    var resize = $('.s-gallery-compare-type-1__resize', panel);
    var divider = $('.s-gallery-compare-type-1__divider', panel);
    var leftWrap = $('.s-gallery-compare-type-1__left-image-wrapper', panel);
    if (!resize || !divider) return;
    divider.style.touchAction = 'none';
    panel.style.touchAction = 'pan-y';

    function fit() { if (leftWrap) leftWrap.style.width = panel.getBoundingClientRect().width + 'px'; }
    function setPos(clientX) {
      var r = panel.getBoundingClientRect();
      var p = Math.min(1, Math.max(0, (clientX - r.left) / r.width)) * 100;
      resize.style.width = p + '%';
      divider.style.left = p + '%';
    }
    var dragging = false;
    divider.addEventListener('pointerdown', function (e) {
      dragging = true;
      try { divider.setPointerCapture(e.pointerId); } catch (_) {}
      e.preventDefault();
    });
    divider.addEventListener('pointermove', function (e) { if (dragging) setPos(e.clientX); });
    ['pointerup', 'pointercancel'].forEach(function (t) {
      divider.addEventListener(t, function () { dragging = false; });
    });
    panel.addEventListener('click', function (e) { setPos(e.clientX); });
    window.addEventListener('resize', fit);
    window.addEventListener('load', fit);
    fit();
  });

  /* 6. Видео YouTube: подгружаем плеер по клику на обложку */
  $$('[data-video="YOUTUBE"]').forEach(function (wrap) {
    var cover = $('.s-video-type-1__file-cover', wrap);
    var frame = $('iframe', wrap);
    if (!cover || !frame) return;
    cover.addEventListener('click', function () {
      var src = frame.getAttribute('data-lazy-src');
      if (src) frame.setAttribute('src', src);
      cover.style.display = 'none';
    });
  });
})();

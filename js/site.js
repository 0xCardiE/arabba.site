(function () {
  'use strict';

  /* --- Skip link focus --- */
  function initSkipLink() {
    var skip = document.querySelector('#skip-link a');
    if (!skip) return;
    skip.addEventListener('click', function (e) {
      var target = document.getElementById('main-content');
      if (!target) return;
      e.preventDefault();
      target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: false });
    });
  }

  /* --- Conversion analytics --- */
  function trackClick(eventName, params) {
    if (typeof gtag === 'function') {
      gtag('event', eventName, params || {});
    }
  }

  function initAnalytics() {
    document.addEventListener('click', function (e) {
      var el = e.target.closest('[data-track], a[href^="tel:"], a[href^="mailto:"], .sticky-call-btn');
      if (!el) return;

      var track = el.getAttribute('data-track');
      if (!track) {
        var href = el.getAttribute('href') || '';
        if (href.indexOf('tel:') === 0) track = el.classList.contains('sticky-call-btn') ? 'sticky_call' : 'phone';
        else if (href.indexOf('mailto:') === 0) track = 'email';
      }
      if (!track) return;

      trackClick(track + '_clicked', {
        link_url: el.getAttribute('href') || undefined,
        link_text: (el.textContent || '').trim().slice(0, 80)
      });
    });
  }

  /* --- Google reviews badge (homepage) --- */
  function renderStars(rating) {
    var roundedHalf = Math.round(rating * 2) / 2;
    var full = Math.floor(roundedHalf);
    var hasHalf = roundedHalf - full >= 0.5;
    var empty = 5 - full - (hasHalf ? 1 : 0);
    var html = '';
    var i;
    for (i = 0; i < full; i++) html += '<span class="star star-full" aria-hidden="true">★</span>';
    if (hasHalf) {
      html += '<span class="star star-half" aria-hidden="true"><span class="star-half-fill">★</span><span class="star-half-bg">☆</span></span>';
    }
    for (i = 0; i < empty; i++) html += '<span class="star star-empty" aria-hidden="true">☆</span>';
    return html;
  }

  function initGoogleReviews() {
    var badge = document.getElementById('google-reviews-badge');
    if (!badge || badge.querySelector('.google-reviews-link')) return;

    fetch('data/google-reviews.json', { cache: 'no-cache' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        if (!data || data.rating == null || data.reviewCount == null) {
          badge.hidden = true;
          return;
        }
        var rating = Number(data.rating);
        var count = Number(data.reviewCount);
        var url = data.googleMapsUrl || '#';
        badge.innerHTML =
          '<a class="google-reviews-link" href="' + url + '" target="_blank" rel="noopener noreferrer" data-track="google_reviews">' +
          '<span class="google-reviews-stars" aria-hidden="true">' + renderStars(rating) + '</span>' +
          '<span class="google-reviews-text">' +
          '<strong>' + rating.toFixed(1).replace('.', ',') + '/5</strong> · ' +
          count + ' Google recenzija</span></a>';
        badge.hidden = false;
      })
      .catch(function () {
        badge.hidden = true;
      });
  }

  /* --- Lazy-load maps and below-fold images --- */
  function initLazyMedia() {
    document.querySelectorAll('iframe[data-src]').forEach(function (iframe) {
      var load = function () {
        if (iframe.getAttribute('src')) return;
        iframe.setAttribute('src', iframe.getAttribute('data-src'));
        iframe.removeAttribute('data-src');
      };
      if ('IntersectionObserver' in window) {
        var obs = new IntersectionObserver(function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              load();
              obs.disconnect();
            }
          });
        }, { rootMargin: '200px' });
        obs.observe(iframe);
      } else {
        load();
      }
    });

    document.querySelectorAll('img:not([loading])').forEach(function (img, i) {
      if (i === 0 || img.closest('#zone-header') || img.id === 'logo') return;
      img.setAttribute('loading', 'lazy');
      img.setAttribute('decoding', 'async');
    });
  }

  function init() {
    initSkipLink();
    initAnalytics();
    initGoogleReviews();
    initLazyMedia();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

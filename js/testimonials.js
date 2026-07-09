(function () {
  var TESTIMONIALS = [
    {
      text: 'Ovim putem Vam želim javiti da sam sve uspješno spojio i upravo Vam šaljem ovaj mail putem računala na kojem ste mi instalirali sve što je bilo potrebno. Zahvaljujem Vam se na suradnji i preporučam se za dalje, ukoliko bude potrebno.',
      name: 'Cvetan Pelčić',
      company: 'Klijent'
    },
    {
      text: 'U redakciji primamo na stotine najava događanja, reporta iz klubova i sa koncerata te se tu nađe i dosta virusa koje se nekada ne mogu izbjeći. Uz Arabba servis svaki put riješim nastale probleme te ga svakom preporučujem.',
      name: 'Leonard Radosavljević',
      company: 'Izlasci.net',
      url: 'http://www.izlasci.net'
    },
    {
      text: 'Laptop mi se stalno gasio i pregrijavao. U Arabbi su brzo pronašli uzrok, očistili sustav hlađenja i sada radi stabilno kao prvog dana.',
      name: 'Marko K.',
      company: 'Klijent, Rijeka'
    },
    {
      text: 'Spasili su mi podatke s pokvarenog diska kad drugi servisi nisu mogli pomoći. Profesionalan pristup, jasna komunikacija i fer cijena.',
      name: 'Ana M.',
      company: 'Klijent'
    },
    {
      text: 'Za naš mali ured održavaju računala već godinama. Pouzdani su, brzo reagiraju i uvijek pronađu rješenje kad nešto zatreba.',
      name: 'Ivica B.',
      company: 'Poslovni korisnik'
    }
  ];

  var INTERVAL_MS = 5000;
  var FADE_MS = 350;

  function render(els, testimonial) {
    els.text.textContent = testimonial.text;
    els.name.textContent = testimonial.name;

    if (testimonial.url) {
      els.company.innerHTML = '<a href="' + testimonial.url + '">' + testimonial.company + '</a>';
    } else {
      els.company.innerHTML = '<span>' + testimonial.company + '</span>';
    }
  }

  function init() {
    var block = document.getElementById('block-views-testimonial-block');
    if (!block) {
      return;
    }

    var els = {
      text: block.querySelector('.views-field-body .field-content p'),
      name: block.querySelector('.views-field-title .field-content'),
      company: block.querySelector('.views-field-field-company-link .field-content'),
      container: block.querySelector('.view-content')
    };

    if (!els.text || !els.name || !els.company) {
      return;
    }

    var index = 0;

    render(els, TESTIMONIALS[index]);

    setInterval(function () {
      if (els.container) {
        els.container.classList.add('is-fading');
      }

      setTimeout(function () {
        index = (index + 1) % TESTIMONIALS.length;
        render(els, TESTIMONIALS[index]);

        if (els.container) {
          els.container.classList.remove('is-fading');
        }
      }, FADE_MS);
    }, INTERVAL_MS);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

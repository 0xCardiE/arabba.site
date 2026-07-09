(function () {
  var TESTIMONIALS = [
    {
      text: 'Ovim putem Vam želim javiti da sam sve uspješno spojio i upravo Vam šaljem ovaj mail putem računala na kojem ste mi instalirali sve što je bilo potrebno. Zahvaljujem Vam se na suradnji i preporučam se za dalje.',
      name: 'Cvetan Pelčić'
    },
    {
      text: 'U redakciji primamo na stotine najava događanja i reporta te se tu nađe i dosta virusa. Uz Arabba servis svaki put riješim nastale probleme te ga svakom preporučujem.',
      name: 'Leonard Radosavljević',
      company: 'Izlasci.net',
      url: 'http://www.izlasci.net'
    },
    {
      text: 'Gospodin Blažeković spasio mi je notebook — ujutro donijet, poslijepodne opet sve radilo. Još jednom veliko hvala.',
      name: 'Sonja'
    },
    {
      text: 'Super usluga, odnio sam subotom i isti dan je bilo popravljeno. Preporuke.',
      name: 'Sven Marenković'
    },
    {
      text: 'Super zadovoljna!',
      name: 'Marina Gulin'
    },
    {
      text: 'Otključao laptop sa zaboravljenom šifrom u par sati bez problema. Sve pohvale za stručnost.',
      name: 'Robo 1788'
    },
    {
      text: 'Vrlo profesionalno, brzo i po povoljnoj cijeni. Sve preporuke!',
      name: 'Sara Barisic'
    },
    {
      text: 'Koristim usluge gosp. Blažekovića godinama i imam samo riječi hvale. Brza intervencija, profesionalnost i dugogodišnje iskustvo.',
      name: 'Igor Ganić'
    },
    {
      text: 'Odlična usluga, brza intervencija i realizacija popravka. Problem riješen u vrlo kratkom roku. Preporučujem!',
      name: 'Korana Stojčić'
    }
  ];

  var INTERVAL_MS = 5000;
  var FADE_MS = 350;

  function render(els, testimonial) {
    els.text.textContent = testimonial.text;
    els.name.textContent = testimonial.name;

    if (testimonial.url && testimonial.company) {
      els.company.innerHTML = '<a href="' + testimonial.url + '">' + testimonial.company + '</a>';
      els.companyField.style.display = '';
    } else {
      els.company.innerHTML = '';
      els.companyField.style.display = 'none';
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
      companyField: block.querySelector('.views-field-field-company-link'),
      container: block.querySelector('.view-content')
    };

    if (!els.text || !els.name || !els.company) {
      return;
    }

    var index = Math.floor(Math.random() * TESTIMONIALS.length);

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

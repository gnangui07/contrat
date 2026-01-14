// orders.js - Version améliorée
document.addEventListener('DOMContentLoaded', function() {
  // Initialisation Select2 avec options améliorées
  if (typeof $ !== 'undefined' && $('#po-search').length) {
    if ($.fn && $.fn.select2 && $.fn.select2.defaults) {
      $.fn.select2.defaults.set('theme', 'bootstrap-5');
    }
    $('#po-search').select2({
      placeholder: 'Rechercher un bon de commande...',
      allowClear: true,
      width: '100%',
      dropdownParent: $('.po-search-form'),
      language: {
        noResults: function() {
          return "Aucun résultat trouvé";
        }
      }
    }).on('change', function() {
      $(this).closest('form').trigger('submit');
    });
  }

  // Animation des cartes au chargement
  $('.card').each(function(i) {
    $(this).delay(i * 100).queue(function() {
      $(this).addClass('animate__animated animate__fadeInUp');
      $(this).dequeue();
    });
  });

  // Tooltips Bootstrap
  $('[data-bs-toggle="tooltip"]').tooltip({
    trigger: 'hover',
    placement: 'top'
  });
});

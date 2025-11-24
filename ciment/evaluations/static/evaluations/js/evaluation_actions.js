// Fonction de confirmation de suppression avec SweetAlert
function confirmDelete(evaluationId, supplierName) {
  Swal.fire({
    title: 'Confirmer la suppression',
    html: `
      <p>Êtes-vous sûr de vouloir supprimer cette évaluation ?</p>
      <div style="background: #f8f9fa; padding: 15px; border-radius: 6px; margin-top: 15px; text-align: left;">
        <p style="margin: 5px 0;"><strong>Fournisseur :</strong> ${supplierName}</p>
      </div>
      <p style="color: #dc3545; margin-top: 15px;"><strong>⚠️ Cette action est irréversible.</strong></p>
    `,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#dc3545',
    cancelButtonColor: '#6c757d',
    confirmButtonText: 'Oui, supprimer',
    cancelButtonText: 'Annuler',
    reverseButtons: true
  }).then((result) => {
    if (result.isConfirmed) {
      // Créer un formulaire et le soumettre
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = `/evaluations/${evaluationId}/delete/`;
      
      // Ajouter le token CSRF
      const csrfCookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
      if (csrfCookie) {
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfCookie.split('=')[1];
        form.appendChild(csrfInput);
      }
      
      document.body.appendChild(form);
      form.submit();
    }
  });
}

// Afficher les messages Django avec SweetAlert
function showDjangoMessages() {
  const messagesContainer = document.getElementById('django-messages-data');
  if (messagesContainer) {
    const messages = JSON.parse(messagesContainer.textContent);
    messages.forEach(message => {
      let icon = 'info';
      let title = 'Information';
      
      if (message.tags === 'success') {
        icon = 'success';
        title = 'Succès';
      } else if (message.tags === 'error') {
        icon = 'error';
        title = 'Erreur';
      } else if (message.tags === 'warning') {
        icon = 'warning';
        title = 'Attention';
      }
      
      Swal.fire({
        icon: icon,
        title: title,
        text: message.message,
        timer: 3000,
        showConfirmButton: false
      });
    });
  }
}

// Initialiser au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
  showDjangoMessages();
  
  // Attacher les événements de suppression
  const deleteButtons = document.querySelectorAll('.delete-evaluation-btn');
  deleteButtons.forEach(button => {
    button.addEventListener('click', function() {
      const evaluationId = this.getAttribute('data-evaluation-id');
      const supplierName = this.getAttribute('data-supplier-name');
      confirmDelete(evaluationId, supplierName);
    });
  });
});

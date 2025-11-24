// SweetAlert confirmation for supplier deletion
function confirmDeleteSupplier(supplierId, supplierName) {
  Swal.fire({
    title: 'Confirmer la suppression',
    html: `
      <p>Êtes-vous sûr de vouloir supprimer ce fournisseur ?</p>
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
      // Create and submit POST form
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = `/suppliers/${supplierId}/delete/`;

      // CSRF from cookie
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

// Display Django messages via SweetAlert (messages passed as JSON in script tag)
function showDjangoMessages() {
  const messagesContainer = document.getElementById('django-messages-data');
  if (!messagesContainer) return;
  try {
    const messages = JSON.parse(messagesContainer.textContent);
    messages.forEach(message => {
      let icon = 'info';
      let title = 'Information';
      if (message.tags === 'success') { icon = 'success'; title = 'Succès'; }
      else if (message.tags === 'error') { icon = 'error'; title = 'Erreur'; }
      else if (message.tags === 'warning') { icon = 'warning'; title = 'Attention'; }
      Swal.fire({ icon, title, text: message.message, timer: 3000, showConfirmButton: false });
    });
  } catch (e) {
    // ignore parse errors
  }
}

// --- ENVOI DE MAIL A PARTIR DE LA LISTE DES FOURNISSEURS ---
function handleMailSupplier(supplierId, supplierName, supplierEmail) {
  Swal.fire({
    icon: 'question',
    title: `<div style='font-size:1.3em;font-weight:bold;margin-bottom:8px;'>Envoi d'email pour <br><span style='color:#2d60c3;'>${supplierName}</span></div>`,
    html: `
      <div style="padding: 2px 2px 0 2px;">
        <div style='margin-bottom:18px; border-left: 4px solid #1070e0; background:#f1f6fa; padding:10px 15px 10px 15px; border-radius:7px;'>
          <span style='font-weight:600;'>Choisissez le ou les types d'email à envoyer :</span><br>
          <div style='margin-top:8px;'>
            <label style='font-weight:500; margin-right: 15px;'><input type='checkbox' id='type-acheteur' checked style='accent-color:#1070e0;'> Acheteur (sourcing)</label>
            <label style='font-weight:500;'><input type='checkbox' id='type-demandeur' style='accent-color:#00bb77;'> Demandeur</label>
          </div>
        </div>
        <div style='margin-bottom:18px; border-left: 4px solid #af9a19; background:#fdfae3; padding:10px 15px 10px 15px; border-radius:7px;'>
          <label style='font-weight:600;'>Emails destinataires</label>
          <input id='input-dest' type='text' placeholder='Ex: acheteur@mail.com, demandeur@email.com' 
            style='margin-top:6px; width:97%; padding:8px 12px; font-size:15px; border-radius:4px; border:1px solid #ccc; box-shadow:0 1px 4px 0 #ebebeb;'>
        </div>
        <div style='margin-bottom:6px; border-left: 4px solid #7735da; background:#f3f0fa; padding:10px 15px 7px 15px; border-radius:7px;'>
          <label style='font-weight:600;'>Méthode d'envoi</label><br>
          <select id='mail-method' style='margin-top:7px;width:98%; padding:8px 12px; border-radius:4px; font-size:15px; border:1px solid #bbb;'>
            <option value='smtp'>Via le serveur sécurisé (SMTP)</option>
            <option value='mailto'>Ouvrir le client mail (Mailto/Gmail…)</option>
          </select>
        </div>
        <div style='margin-top:13px; text-align:center; font-size:1em; color:#969393;'>
          <i class="bx bx-info-circle"></i> Le contenu du mail s'adapte automatiquement à votre choix !
        </div>
      </div>
    `,
    customClass: {
      title: 'swal2-title',
      confirmButton: 'swal2-confirm swal2-styled',
      cancelButton: 'swal2-cancel swal2-styled'
    },
    confirmButtonText: '<i class="bx bx-send"></i> Envoyer',
    cancelButtonText: 'Annuler',
    showCancelButton: true,
    focusConfirm: false,
    preConfirm: () => {
      const types = [];
      if (document.getElementById('type-acheteur').checked) types.push('acheteur');
      if (document.getElementById('type-demandeur').checked) types.push('demandeur');
      const dest = document.getElementById('input-dest').value.trim();
      const method = document.getElementById('mail-method').value;
      if (types.length === 0) {
        Swal.showValidationMessage('Choisissez au moins un type de mail');
        return false;
      }
      if (!dest.match(/^([\w.-]+@[\w.-]+(,\s*|\s*)?)+$/)) {
        Swal.showValidationMessage('Entrez au moins un email valide (séparés par des virgules si besoin)');
        return false;
      }
      return { types, dest, method };
    },
    didOpen: () => {
      setTimeout(() => {
        const input = document.getElementById('input-dest');
        if (input) input.focus();
      }, 100);
    }
  }).then((result) => {
    if (result.isConfirmed && result.value) {
      const types = result.value.types;
      const dest = result.value.dest;
      const method = result.value.method;
      if (method === 'mailto') {
        fetch(`/suppliers/${supplierId}/get_eval_summary/?types=${types.join(',')}`)
          .then(r => r.json())
          .then(data => {
            if (data.error) {
              Swal.fire('Envoi impossible', data.error, 'warning');
              return;
            }
            let subject = encodeURIComponent('Evaluation fournisseur : ' + supplierName);
            let body = '';
            if (data && data.text_body) {
              body = encodeURIComponent(data.text_body);
            } else {
              body = encodeURIComponent('Bonjour,\n\nDétail indisponible.');
            }
            window.location.href = `mailto:${dest}?subject=${subject}&body=${body}`;
          });
      } else {
        // Appel AJAX au backend pour gestion SMTP
        fetch(`/suppliers/${supplierId}/send_mail/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.cookie.split('; ').find(r => r.startsWith('csrftoken=')).split('=')[1],
          },
          body: JSON.stringify({ types, dest, supplierId })
        })
        .then(r => r.json())
        .then(data => {
          if (data.success) {
            Swal.fire('Succès', 'Email envoyé avec succès !', 'success');
          } else {
            Swal.fire('Erreur', data.error || "L'envoi n'a pas abouti", 'error');
          }
        })
        .catch(() => Swal.fire('Erreur', "Problème réseau/l'envoi a échoué", 'error'));
      }
    }
  });
}

// Init
document.addEventListener('DOMContentLoaded', function () {
  showDjangoMessages();
  document.querySelectorAll('.delete-supplier-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const supplierId = this.getAttribute('data-supplier-id');
      const supplierName = this.getAttribute('data-supplier-name');
      confirmDeleteSupplier(supplierId, supplierName);
    });
  });
  document.querySelectorAll('.mail-supplier-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const supplierId = this.getAttribute('data-supplier-id');
      const supplierName = this.getAttribute('data-supplier-name');
      const supplierEmail = this.getAttribute('data-supplier-email');
      handleMailSupplier(supplierId, supplierName, supplierEmail);
    });
  });
});

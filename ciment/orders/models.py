from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from suppliers.models import Supplier


class PurchaseOrder(models.Model):
    number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Numéro de bon de commande",
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Fournisseur",
        related_name="purchase_orders",
    )

    # Champs d'en-tête importés depuis le fichier (métadonnées PO)
    release_indicator = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Release indicator",
    )
    document_date = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Document Date",
    )
    purchasing_group = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Purchasing Group",
    )
    release_date = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Release Date",
    )
    created_by = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name="Created By",
    )

    _total_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Montant total (cache)",
    )
    _received_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Montant reçu (cache)",
    )
    _remaining_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Montant restant (cache)",
    )
    _progress_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Taux d'avancement (%) (cache)",
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Bon de commande"
        verbose_name_plural = "Bons de commande"
        ordering = ["number"]

    def __str__(self):
        return str(self.number)

    def _compute_amounts(self):
        total_amount = Decimal("0")
        received_amount = Decimal("0")
        remaining_amount = Decimal("0")

        for line in self.lines.all():
            total_amount += line.get_line_total_amount()
            received_amount += line.get_line_received_amount()
            remaining_amount += line.get_line_remaining_amount()

        if total_amount > 0:
            progress_rate = (received_amount / total_amount) * Decimal("100")
        else:
            progress_rate = Decimal("0")

        self._total_amount = total_amount
        self._received_amount = received_amount
        self._remaining_amount = remaining_amount
        self._progress_rate = progress_rate

    def update_amounts(self, save=True):
        self._compute_amounts()
        if save:
            self.save(
                update_fields=[
                    "_total_amount",
                    "_received_amount",
                    "_remaining_amount",
                    "_progress_rate",
                    "updated_at",
                ]
            )

    def get_total_amount(self):
        if self._total_amount is None:
            self.update_amounts(save=False)
        return self._total_amount or Decimal("0")

    def get_received_amount(self):
        if self._received_amount is None:
            self.update_amounts(save=False)
        return self._received_amount or Decimal("0")

    def get_remaining_amount(self):
        if self._remaining_amount is None:
            self.update_amounts(save=False)
        return self._remaining_amount or Decimal("0")

    def get_progress_rate(self):
        if self._progress_rate is None:
            self.update_amounts(save=False)
        return self._progress_rate or Decimal("0")

    def get_currency(self):
        """Retourne la devise du bon de commande.

        On prend la devise de la première ligne non nulle/non vide.
        La requête est filtrée côté base, donc même avec beaucoup de lignes,
        on ne charge qu'un seul enregistrement.
        """
        first_line = (
            self.lines.exclude(currency__isnull=True)
            .exclude(currency__exact="")
            .only("currency")
            .first()
        )
        return first_line.currency if first_line else None


class PurchaseOrderLine(models.Model):
    business_id = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="ID métier (PO + Item)",
    )

    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name="Bon de commande",
    )

    purchasing_document = models.CharField(
        max_length=100,
        verbose_name="Purchasing Document",
    )
    item = models.CharField(
        max_length=50,
        verbose_name="Item",
    )

    # Champs de détail supplémentaires importés
    material = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Material",
    )
    short_text = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Short Text",
    )
    order_unit = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Order Unit",
    )
    currency = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name="Currency",
    )

    net_order_value = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Net Order Value",
    )
    order_quantity = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Order Quantity",
    )
    net_price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Net Price",
    )
    received_quantity = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Received Quantity",
    )
    still_to_be_delivered_qty = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Still to be delivered (qty)",
    )

    class Meta:
        verbose_name = "Ligne de bon de commande"
        verbose_name_plural = "Lignes de bon de commande"
        ordering = ["purchasing_document", "item"]

    def __str__(self):
        return f"{self.purchasing_document} / {self.item}"

    @classmethod
    def generate_business_id(cls, purchasing_document, item):
        doc = (str(purchasing_document) or "").strip()
        raw_item = str(item).strip()
        padded_item = raw_item.zfill(4) if raw_item else ""
        return f"{doc}-{padded_item}"

    def get_line_total_amount(self):
        return self.net_order_value or Decimal("0")

    def get_line_received_amount(self):
        if self.received_quantity is None or self.net_price is None:
            return Decimal("0")
        return (self.received_quantity or Decimal("0")) * (self.net_price or Decimal("0"))

    def get_line_remaining_amount(self):
        if self.still_to_be_delivered_qty is None or self.net_price is None:
            return Decimal("0")
        return (self.still_to_be_delivered_qty or Decimal("0")) * (self.net_price or Decimal("0"))


class ImportedFile(models.Model):
    """Fichier importé contenant des bons de commande.

    Sert uniquement de support d'upload et de traçabilité. Les PurchaseOrder
    et PurchaseOrderLine créés à partir de ce fichier NE dépendent pas de
    l'existence future du fichier.
    """

    file = models.FileField(
        upload_to="orders/imports/",
        verbose_name="Fichier importé",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        verbose_name="Utilisateur",
    )
    extension = models.CharField(
        max_length=10,
        editable=False,
        verbose_name="Extension",
    )
    imported_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name="Date d'import",
    )
    rows_count = models.IntegerField(
        default=0,
        editable=False,
        verbose_name="Nombre de lignes",
    )

    class Meta:
        verbose_name = "Fichier importé"
        verbose_name_plural = "Fichiers importés"
        ordering = ["-imported_at"]

    def __str__(self):
        return f"{self.file.name} ({self.imported_at:%Y-%m-%d %H:%M})"



# Create your models here.

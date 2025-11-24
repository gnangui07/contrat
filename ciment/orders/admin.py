from django.contrib import admin, messages

from .models import ImportedFile, PurchaseOrder, PurchaseOrderLine
from .services import import_purchase_orders_from_excel


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "get_total_amount",
        "get_received_amount",
        "get_remaining_amount",
        "get_progress_rate",
        "created_at",
    )
    search_fields = ("number",)
    ordering = ("number",)


@admin.register(PurchaseOrderLine)
class PurchaseOrderLineAdmin(admin.ModelAdmin):
    list_display = (
        "business_id",
        "purchasing_document",
        "item",
        "net_order_value",
        "order_quantity",
        "net_price",
        "received_quantity",
        "still_to_be_delivered_qty",
    )
    search_fields = ("business_id", "purchasing_document", "item")
    list_filter = ("purchasing_document",)


@admin.register(ImportedFile)
class ImportedFileAdmin(admin.ModelAdmin):
    list_display = ("file", "user", "extension", "rows_count", "imported_at")
    readonly_fields = ("user", "extension", "rows_count", "imported_at")
    date_hierarchy = "imported_at"

    def save_model(self, request, obj, form, change):
        # Sauvegarde initiale pour disposer du fichier sur le disque/storage
        is_new = obj.pk is None

        # Récupérer automatiquement l'utilisateur qui importe
        if not obj.user:
            obj.user = request.user if request.user.is_authenticated else None
        super().save_model(request, obj, form, change)

        if not obj.file:
            return

        # Détecter l'extension simple (sans le point)
        from os.path import splitext

        _, ext = splitext(obj.file.name)
        obj.extension = ext.lstrip(".").lower()

        # Lancer l'import depuis le fichier
        try:
            summary = import_purchase_orders_from_excel(obj.file, imported_file=obj)
            obj.save(update_fields=["extension", "rows_count"])

            messages.success(
                request,
                (
                    "Import terminé: "
                    f"{summary.get('lines_processed', 0)} lignes, "
                    f"{summary.get('pos_created', 0)} PO créés, "
                    f"{summary.get('pos_updated', 0)} PO mis à jour."
                ),
            )

            errors = summary.get("errors") or []
            if errors:
                # Afficher un seul message warning global, les détails restent dans les logs
                messages.warning(
                    request,
                    f"Certaines lignes ont été ignorées ({len(errors)}). Voir les logs pour le détail.",
                )
        except Exception as exc:
            messages.error(request, f"Erreur lors de l'import du fichier: {exc}")


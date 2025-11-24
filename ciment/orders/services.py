from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import pandas as pd

from django.db import transaction

from .models import PurchaseOrder, PurchaseOrderLine
from suppliers.models import Supplier


def round_decimal(value: Any, places: int = 2) -> Decimal:
    """Arrondit une valeur décimale au nombre de décimales spécifié.

    :param value: Decimal, float, int, str ou None
    :param places: Nombre de décimales (par défaut 2)
    :return: Decimal arrondi
    """
    if value is None:
        return Decimal("0")
    if not isinstance(value, Decimal):
        try:
            value = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return Decimal("0")

    if places <= 0:
        quant_format = Decimal("1")
    else:
        quant_format = Decimal("0." + ("0" * (places - 1)) + "1")

    return value.quantize(quant_format, rounding=ROUND_HALF_UP)


def clean_text(value: Any) -> Optional[str]:
    """Nettoie une valeur texte issue de pandas/import.

    - Convertit les NaN/NaT en None
    - Trim les espaces
    - Remplace les chaînes vides ou 'nan'/'nat'/'null'/'none' par None
    """
    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except Exception:
        # Si pd.isna ne sait pas gérer le type, on continue avec la logique string
        pass

    text = str(value).strip()
    if not text:
        return None

    lower = text.lower()
    if lower in {"nan", "nat", "none", "null"}:
        return None

    return text


def normalize_header(header: str) -> str:
    """Normalise un nom de colonne en format canonique.

    - strip
    - lower
    - remplace '_' et '-' par des espaces
    - compresse les espaces multiples
    """
    if header is None:
        return ""
    text = str(header).strip().lower()
    text = text.replace("_", " ").replace("-", " ")
    parts = [p for p in text.split() if p]
    return " ".join(parts)


def get_value_tolerant(
    row: Dict[str, Any],
    exact_candidates: Optional[Sequence[str]] = None,
    tokens: Optional[Sequence[str]] = None,
) -> Any:
    """Récupère une valeur dans un dict en étant tolérant sur le nom de colonne.

    - Construit un mapping de clés normalisées -> (clé originale, valeur)
    - Tente d'abord les exact_candidates (normalisés)
    - Sinon, utilise les tokens (tous présents dans la clé normalisée)
    """
    if not row:
        return None

    normalized: Dict[str, Tuple[str, Any]] = {}
    for original_key, value in row.items():
        if original_key is None:
            continue
        norm = normalize_header(original_key)
        if norm and norm not in normalized:
            normalized[norm] = (original_key, value)

    # 1) Essayer les candidats exacts
    if exact_candidates:
        for candidate in exact_candidates:
            norm_candidate = normalize_header(candidate)
            if norm_candidate in normalized:
                return normalized[norm_candidate][1]

    # 2) Essayer la recherche par tokens
    if tokens:
        norm_tokens = [normalize_header(t) for t in tokens if t]
        norm_tokens = [t for t in norm_tokens if t]
        for norm_key, (_orig, value) in normalized.items():
            if all(t in norm_key for t in norm_tokens):
                return value

    return None


def normalize_keys(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Unifie les noms de colonnes sur toute une liste de dicts.

    Retourne une nouvelle liste de dicts avec les mêmes clés canonisées.
    """
    rows = list(rows)
    if not rows:
        return []

    canonical_keys: Dict[str, str] = {}

    # Construire la table de correspondance des clés
    for row in rows:
        for key in row.keys():
            norm = normalize_header(key)
            if norm and norm not in canonical_keys:
                canonical_keys[norm] = key

    normalized_rows: List[Dict[str, Any]] = []
    for row in rows:
        new_row: Dict[str, Any] = {}
        for key, value in row.items():
            norm = normalize_header(key)
            if norm:
                # On réutilise toujours la même clé canonique (la première rencontrée)
                canonical = canonical_keys.get(norm, key)
                new_row[canonical] = value
        normalized_rows.append(new_row)

    return normalized_rows


@transaction.atomic
def import_purchase_orders_from_excel(uploaded_file, imported_file: Optional[object] = None) -> Dict[str, Any]:
    """Importe un fichier Excel et alimente PurchaseOrder / PurchaseOrderLine.

    - Lit le fichier avec pandas
    - Normalise les clés
    - Utilise business_id = Purchasing Document + Item
    - Crée / met à jour les lignes et les PO
    """
    # 1) Lire le fichier avec pandas
    try:
        df = pd.read_excel(uploaded_file)
    except Exception:
        # Tentative de lecture CSV en fallback
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file)

    records = df.to_dict(orient="records")
    records = normalize_keys(records)

    lines_processed = 0
    pos_created = 0
    pos_updated = 0
    errors: List[str] = []

    affected_pos: Dict[str, PurchaseOrder] = {}

    for row in records:
        # Extraire les valeurs brutes avec recherche tolérante
        purchasing_document = get_value_tolerant(
            row,
            exact_candidates=["Purchasing Document", "PO Number", "Purchasing Doc"],
            tokens=["purchasing", "document"],
        )
        item = get_value_tolerant(
            row,
            exact_candidates=["Item", "Item Number", "Item No."],
            tokens=["item"],
        )

        if not purchasing_document or item in (None, ""):
            # Ligne inutilisable pour notre logique : on loggue et on skip
            errors.append("Ligne ignorée: Purchasing Document ou Item manquant")
            continue

        purchasing_document = str(purchasing_document).strip()
        item_str = str(item).strip()

        # Champs numériques
        net_order_value_raw = get_value_tolerant(
            row,
            exact_candidates=["Net Order Value", "Net Value"],
            tokens=["net", "value"],
        )
        order_quantity_raw = get_value_tolerant(
            row,
            exact_candidates=["Order Quantity", "Quantity", "Qty"],
            tokens=["order", "quantity"],
        )
        net_price_raw = get_value_tolerant(
            row,
            exact_candidates=["Net Price", "Unit Price"],
            tokens=["price"],
        )
        received_quantity_raw = get_value_tolerant(
            row,
            exact_candidates=["Received Quantity", "Received Qty"],
            tokens=["received", "quantity"],
        )
        still_to_be_delivered_raw = get_value_tolerant(
            row,
            exact_candidates=[
                "Still to be delivered (qty)",
                "Still to be delivered qty",
                "Remaining Qty",
            ],
            tokens=["still", "delivered"],
        )

        # Champs texte supplémentaires (en-tête et ligne)
        release_indicator_raw = get_value_tolerant(
            row,
            exact_candidates=["Release indicator"],
            tokens=["release", "indicator"],
        )
        document_date_raw = get_value_tolerant(
            row,
            exact_candidates=["Document Date"],
            tokens=["document", "date"],
        )
        purchasing_group_raw = get_value_tolerant(
            row,
            exact_candidates=["Purchasing Group"],
            tokens=["purchasing", "group"],
        )
        release_date_raw = get_value_tolerant(
            row,
            exact_candidates=["Release Date"],
            tokens=["release", "date"],
        )
        created_by_raw = get_value_tolerant(
            row,
            exact_candidates=["Created By"],
            tokens=["created", "by"],
        )

        material_raw = get_value_tolerant(
            row,
            exact_candidates=["Material"],
            tokens=["material"],
        )
        short_text_raw = get_value_tolerant(
            row,
            exact_candidates=["Short Text"],
            tokens=["short", "text"],
        )
        order_unit_raw = get_value_tolerant(
            row,
            exact_candidates=["Order Unit"],
            tokens=["order", "unit"],
        )
        currency_raw = get_value_tolerant(
            row,
            exact_candidates=["Currency"],
            tokens=["currency"],
        )

        net_order_value = round_decimal(net_order_value_raw)
        order_quantity = round_decimal(order_quantity_raw)
        net_price = round_decimal(net_price_raw)
        received_quantity = round_decimal(received_quantity_raw)
        still_to_be_delivered_qty = round_decimal(still_to_be_delivered_raw)

        # 2) Récupérer ou créer le Supplier depuis Name of Supplier
        supplier_name_raw = get_value_tolerant(
            row,
            exact_candidates=["Name of Supplier", "Supplier", "Vendor"],
            tokens=["supplier"],
        )

        supplier_obj = None
        supplier_name = clean_text(supplier_name_raw)
        if supplier_name:
            # On matche sur nom_complet_organisation, création minimale si besoin
            supplier_obj, _ = Supplier.objects.get_or_create(
                nom_complet_organisation=supplier_name,
                defaults={
                    # Valeurs minimales / factices, à compléter ensuite dans le module suppliers
                    "type_fournisseur": "Local",
                    "type_organisation": "SA",
                    "date_enregistrement": "2000-01-01",
                    "adresse_physique": "",
                    "telephone": "",
                    "email": "",
                    "nom_representant_legal": "",
                    "fonction_representant": "",
                    "personne_contact": "",
                    "telephone_contact": "",
                    "email_contact": "",
                    "registre_commerce": "",
                    "numero_compte_contribuable": "",
                    "attestation_regularite_fiscale": "",
                    "numero_cnps": "",
                    "banque": "",
                    "agence": "",
                    "iban": "",
                    "modalite_paiement": "Net 30",
                    "type_categorie": "Autres",
                    "categorie": "Autres",
                    "description_categorie": "Import automatique depuis fichier PO",
                },
            )

        # 3) Récupérer ou créer le PurchaseOrder
        po, created = PurchaseOrder.objects.get_or_create(number=purchasing_document)

        header_changed = False
        if supplier_obj and po.supplier_id is None:
            po.supplier = supplier_obj
            header_changed = True

        # Nettoyer d'éventuelles anciennes valeurs invalides ('nan', 'NaT', etc.)
        for field in [
            "release_indicator",
            "document_date",
            "purchasing_group",
            "release_date",
            "created_by",
        ]:
            current = getattr(po, field)
            if current is not None and clean_text(current) is None:
                setattr(po, field, None)
                header_changed = True

        # Renseigner les champs d'en-tête importés (sans écraser si déjà présents)
        value = clean_text(release_indicator_raw)
        if value and not po.release_indicator:
            po.release_indicator = value
            header_changed = True
        value = clean_text(document_date_raw)
        if value and not po.document_date:
            po.document_date = value
            header_changed = True
        value = clean_text(purchasing_group_raw)
        if value and not po.purchasing_group:
            po.purchasing_group = value
            header_changed = True
        value = clean_text(release_date_raw)
        if value and not po.release_date:
            po.release_date = value
            header_changed = True
        value = clean_text(created_by_raw)
        if value and not po.created_by:
            po.created_by = value
            header_changed = True

        if header_changed:
            po.save()
        if created:
            pos_created += 1
        else:
            pos_updated += 1
        affected_pos[purchasing_document] = po

        # 3) Générer business_id et créer / mettre à jour la ligne
        business_id = PurchaseOrderLine.generate_business_id(purchasing_document, item_str)

        line, created_line = PurchaseOrderLine.objects.get_or_create(
            business_id=business_id,
            defaults={
                "purchase_order": po,
                "purchasing_document": purchasing_document,
                "item": item_str,
                "material": clean_text(material_raw),
                "short_text": clean_text(short_text_raw),
                "order_unit": clean_text(order_unit_raw),
                "currency": clean_text(currency_raw),
                "net_order_value": net_order_value,
                "order_quantity": order_quantity,
                "net_price": net_price,
                "received_quantity": received_quantity,
                "still_to_be_delivered_qty": still_to_be_delivered_qty,
            },
        )

        if not created_line:
            # Mettre à jour les valeurs numériques et le lien PO si besoin
            line.purchase_order = po
            line.purchasing_document = purchasing_document
            line.item = item_str
            if material_raw is not None:
                line.material = clean_text(material_raw)
            if short_text_raw is not None:
                line.short_text = clean_text(short_text_raw)
            if order_unit_raw is not None:
                line.order_unit = clean_text(order_unit_raw)
            if currency_raw is not None:
                line.currency = clean_text(currency_raw)
            line.net_order_value = net_order_value
            line.order_quantity = order_quantity
            line.net_price = net_price
            line.received_quantity = received_quantity
            line.still_to_be_delivered_qty = still_to_be_delivered_qty
            line.save()

        lines_processed += 1

    # 4) Mettre à jour les montants des PO impactés
    for po in affected_pos.values():
        po.update_amounts(save=True)

    summary = {
        "lines_processed": lines_processed,
        "pos_created": pos_created,
        "pos_updated": pos_updated,
        "errors": errors,
    }

    # Optionnel: si on veut stocker rows_count sur ImportedFile quand on passe imported_file
    if imported_file is not None:
        try:
            imported_file.rows_count = lines_processed
            imported_file.save(update_fields=["rows_count"])
        except Exception:
            # On ne casse pas l'import si l'update échoue
            pass

    return summary

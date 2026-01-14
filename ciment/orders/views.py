from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import PurchaseOrder

# Create your views here.

def purchase_order_list(request):
    qs = PurchaseOrder.objects.all().order_by("number")

    q = request.GET.get("q")
    if q:
        qs = qs.filter(number__icontains=q)

    suggestions = PurchaseOrder.objects.all().order_by("-created_at")[:20]

    paginator = Paginator(qs, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": q or "",
        "suggestions": suggestions,
    }
    return render(request, "orders/purchaseorder_list.html", context)


def purchase_order_detail(request, number):
    po = get_object_or_404(PurchaseOrder, number=number)
    lines = po.lines.all().order_by("item")

    context = {
        "purchase_order": po,
        "lines": lines,
        "total_amount": po.get_total_amount(),
        "received_amount": po.get_received_amount(),
        "remaining_amount": po.get_remaining_amount(),
        "progress_rate": po.get_progress_rate(),
    }
    return render(request, "orders/purchaseorder_detail.html", context)

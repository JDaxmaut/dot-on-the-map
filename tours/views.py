from django.shortcuts import render
from django.db.models import Q

from .models import TourPage


def search(request):
    q = request.GET.get("q", "").strip()
    results = TourPage.objects.none()
    if len(q) >= 2:
        results = (
            TourPage.objects.live()
            .filter(Q(title__icontains=q) | Q(summary__icontains=q) | Q(location__icontains=q))
            .order_by("title")
        )
    return render(request, "search.html", {"q": q, "results": results})

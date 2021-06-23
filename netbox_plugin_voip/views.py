# views.py
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404, render
from django.views import View

from .models import DIDNumbers

class VOIPView(View):
    # Display VOIP page
    queryset = DIDNumbers.objects.all()

    def get(self, request, pk):
        """Get request."""
        voipview_obj = get_object_or_404(self.queryset, pk=pk)

        return render(
            request,
            "netbox_plugin_voip/voipview.html",
            {
                "voipview": voipview_obj,
            },
        )
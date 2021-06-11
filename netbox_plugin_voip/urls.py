from django.http import HttpResponse
from django.urls import path


def dummy_view(request):
    html = "<html><body>Call Routing</body></html>"
    return HttpResponse(html)


urlpatterns = [
    path("", dummy_view, name="netbox_plugin_voip"),
]

from netbox_plugin_voip.views import PartitionView, VOIPView
from django.http import HttpResponse
from django.urls import path


def dummy_view(request):
    html = "<html><body>Call Routing</body></html>"
    return HttpResponse(html)

# These urlpatterns are referenced in navigation.py
urlpatterns = [
    path("", dummy_view, name="voice-main-page"),
    path("<int:pk>/", VOIPView.as_view(), name="voipview")
]

from django.http import HttpResponse
from django.urls import path


def dummy_view(request):
    html = "<html><body>Call Routing</body></html>"
    return HttpResponse(html)

# These urlpatterns are referenced in navigation.py
urlpatterns = [
    path("", dummy_view, name="voice-main-page"),
]

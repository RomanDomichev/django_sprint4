# blogicum/pages/urls.py
from django.urls import path
from .views import AboutView, RulesView, csrf_failure, custom_404, custom_500

app_name = 'pages'

urlpatterns = [
    path('about/', AboutView.as_view(), name='about'),
    path('rules/', RulesView.as_view(), name='rules'),
]
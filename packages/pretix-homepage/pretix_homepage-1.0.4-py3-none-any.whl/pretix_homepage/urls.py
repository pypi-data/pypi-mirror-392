from django.urls import re_path

from .views import about_view, contact_view, index_view, policy_view

urlpatterns = [
    re_path(r"^$", index_view, name="index"),
    re_path(r"^about/", about_view, name="about"),
    re_path(r"^contact/", contact_view, name="contact"),
    re_path(r"^policy/", policy_view, name="policy"),
]

import logging
from django.shortcuts import render
from pretix.base.models import Organizer
from pretix.helpers.urls import build_absolute_uri

logger = logging.getLogger("pretix.plugins.homepage")


def index_view(request, *args, **kwargs):
    logger.debug("rendering home page")

    organizers = list(Organizer.objects.values("name", "slug"))
    for org in organizers:
        org["url"] = build_absolute_uri(
            "presale:organizer.index", kwargs={"organizer": org["slug"]}
        )
    logger.debug("orgs: %s", organizers)

    r = render(request, "pretix_homepage/index.html", {"organizers": organizers})
    r._csp_ignore = True
    return r


def about_view(request, *args, **kwargs):
    return render(request, "pretix_homepage/about.html")


def contact_view(request, *args, **kwargs):
    return render(request, "pretix_homepage/contact.html")


def policy_view(request, *args, **kwargs):
    return render(request, "pretix_homepage/policy.html")

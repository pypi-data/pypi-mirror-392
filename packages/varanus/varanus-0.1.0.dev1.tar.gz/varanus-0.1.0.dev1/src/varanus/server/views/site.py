from typing import ClassVar

from django.contrib.contenttypes.models import ContentType
from django.db.models import OuterRef, QuerySet, Subquery

from ..models import Context
from ..search import DateRange, MultiFacet, Search
from .base import SiteView


class Overview(SiteView):
    template_name = "site/overview.html"

    def get_context(self):
        nodes = self.site.nodes.annotate(
            last_event=Subquery(
                Context.objects.filter(node_id=OuterRef("id"))
                .order_by("-timestamp")
                .values("timestamp")[:1]
            ),
        )
        return {
            "host": self.request.get_host(),
            "scheme": self.request.scheme,
            "nodes": nodes,
        }


class SearchView(SiteView):
    search_class: ClassVar[type[Search]]

    def get_queryset(self) -> QuerySet:
        raise NotImplementedError()

    def get_context(self):
        search = self.search_class(self.get_queryset(), self.request.GET)
        return {
            "search": search,
            "results": search.queryset(),
        }


class Logs(SearchView):
    template_name = "site/logs.html"

    class search_class(Search):
        timeframe = DateRange(field_name="timestamp")
        name = MultiFacet()
        level = MultiFacet()

    def get_queryset(self) -> QuerySet:
        return self.site.logs.select_related("context")


class Errors(SearchView):
    template_name = "site/errors.html"

    class search_class(Search):
        timeframe = DateRange(field_name="timestamp")
        kind = MultiFacet()
        module = MultiFacet()

    def get_queryset(self) -> QuerySet:
        return self.site.errors.select_related("context")


class Requests(SearchView):
    template_name = "site/requests.html"

    class search_class(Search):
        timeframe = DateRange(field_name="timestamp")
        status = MultiFacet()

    def get_queryset(self) -> QuerySet:
        return self.site.requests.select_related("context")


class Queries(SearchView):
    template_name = "site/queries.html"

    class search_class(Search):
        timeframe = DateRange(field_name="timestamp")
        type = MultiFacet(field_name="command")
        db = MultiFacet()

    def get_queryset(self) -> QuerySet:
        return self.site.queries.select_related("context")


class Metrics(SearchView):
    template_name = "site/metrics.html"

    class search_class(Search):
        timeframe = DateRange(field_name="timestamp")
        name = MultiFacet()

    def get_queryset(self) -> QuerySet:
        return self.site.metrics.select_related("context")


class Details(SiteView):
    @property
    def template_name(self):
        model = self.kwargs["model"]
        return f"site/details/{model}.html"

    def get_context(self):
        ct = ContentType.objects.get_by_natural_key("varanus", self.kwargs["model"])
        obj = ct.get_object_for_this_type(pk=self.kwargs["pk"])
        return {
            "object": obj,
        }

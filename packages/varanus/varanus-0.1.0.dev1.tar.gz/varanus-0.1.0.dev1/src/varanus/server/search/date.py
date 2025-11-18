import datetime

from django.db.models import QuerySet
from django.utils.dateparse import parse_date

from .base import SearchField, StringValues


def date_value(field_data: StringValues, name: str) -> datetime.date | None:
    if name not in field_data:
        return None
    if not field_data[name]:
        return None
    return parse_date(field_data[name][0])


class DateRange(SearchField):
    template_name = "search/daterange.html"

    def apply(self, queryset: QuerySet, field_data: StringValues) -> QuerySet:
        filters = {}
        if start := date_value(field_data, "start"):
            filters[f"{self.field_name}__date__gte"] = start
        if end := date_value(field_data, "end"):
            filters[f"{self.field_name}__date__lte"] = end
        return queryset.filter(**filters)

    def get_context(self, queryset: QuerySet, field_data: StringValues) -> dict:
        return {
            **super().get_context(queryset, field_data),
            "start": date_value(field_data, "start"),
            "end": date_value(field_data, "end"),
        }

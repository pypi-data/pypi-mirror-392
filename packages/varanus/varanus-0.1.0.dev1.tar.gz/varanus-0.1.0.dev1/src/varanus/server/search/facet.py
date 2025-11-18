from typing import Any, ClassVar

from django.db.models import Count, QuerySet

from .base import SearchField, StringValues


class Choice:
    id: str
    value: str
    label: str
    count: int

    def __init__(self, field: SearchField, value: Any):
        self.value = self.stringify(value)
        self.label = self.value
        self.id = field.id + "_" + self.value.replace(" ", "")
        self.count = 0

    @classmethod
    def stringify(cls, value):
        return str(value)


class Facet(SearchField):
    choice_class: ClassVar[type[Choice]] = Choice

    def get_choices(self, queryset, with_counts=True):
        choices = [
            self.choice_class(self, c)
            for c in queryset.order_by(self.field_name)
            .values_list(self.field_name, flat=True)
            .distinct(self.field_name)
        ]
        if with_counts:
            counts = {
                self.choice_class.stringify(r[self.field_name]): r["num"]
                for r in queryset.values(self.field_name).annotate(num=Count("*"))
            }
            for c in choices:
                c.count = counts.get(c.value, 0)
        return choices


class MultiFacet(Facet):
    template_name = "search/multifacet.html"

    def apply(self, queryset: QuerySet, field_data: StringValues) -> QuerySet:
        filters = {}
        if selected := field_data.get("s", []):
            filters[f"{self.field_name}__in"] = selected
        return queryset.filter(**filters)

    def get_context(self, queryset: QuerySet, field_data: StringValues) -> dict:
        return {
            **super().get_context(queryset, field_data),
            "choices": self.get_choices(queryset),
            "selected": field_data.get("s", []),
        }

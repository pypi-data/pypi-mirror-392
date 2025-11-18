from typing import ClassVar, Mapping, Self

from django.db.models import QuerySet
from django.http import HttpRequest
from django.template import loader
from django.utils.datastructures import MultiValueDict

type StringValues = dict[str, list[str]]


def string_data(data) -> StringValues:
    if isinstance(data, MultiValueDict):
        return {str(key): [str(v) for v in values] for key, values in data.lists()}
    elif isinstance(data, Mapping):
        return {
            str(key): (
                [str(v) for v in values]
                if isinstance(values, (list, tuple))
                else ([] if values is None else [str(values)])
            )
            for key, values in data.items()
        }
    return {}


class SearchField:
    template_name: str

    def __init__(self, label=None, field_name=None):
        self.name = ""
        self.label = label or ""
        self.field_name = field_name or ""
        self.prefix = ""
        self.id = ""

    def __set_name__(self, owner, name: str):
        # print("__set_name__", owner, name)
        assert issubclass(owner, Search)
        self.name = name
        self.prefix = f"{name}_"
        self.id = f"id_{name}"
        if not self.label:
            self.label = name.capitalize()
        if not self.field_name:
            self.field_name = name
        if not hasattr(owner, "_fields"):
            owner._fields = []
        owner._fields.append(self)

    def __get__(self, instance: "Search", owner=None) -> StringValues | Self:
        # print("__get__", instance, owner)
        if owner is None:
            return self
        return {
            key[len(self.prefix) :]: values
            for key, values in instance._data.items()
            if key.startswith(self.prefix)
        }

    def __set__(self, instance, value):
        print("__set__", instance, value)

    def apply(self, queryset: QuerySet, field_data: StringValues) -> QuerySet:
        raise NotImplementedError()

    def get_context(self, queryset: QuerySet, field_data: StringValues) -> dict:
        return {
            "field": self,
        }

    def render(
        self,
        queryset: QuerySet,
        field_data: StringValues,
        request: HttpRequest | None = None,
    ) -> str:
        return loader.render_to_string(
            self.template_name,
            self.get_context(queryset, field_data),
            request,
        )


class Search:
    _fields: ClassVar[list[SearchField]]

    def __init__(self, queryset: QuerySet, data=None):
        self._queryset = queryset
        self._data = string_data(data)

    def queryset(self, for_field=None):
        qs = self._queryset
        for field in self._fields:
            if field == for_field:
                continue
            field_data = getattr(self, field.name)
            qs = field.apply(qs, field_data)
        return qs

    def render(self, request: HttpRequest | None = None) -> str:
        fragments = []
        for field in self._fields:
            qs = self.queryset(for_field=field)
            field_data = getattr(self, field.name)
            fragments.append(field.render(qs, field_data, request))
        return "".join(fragments)

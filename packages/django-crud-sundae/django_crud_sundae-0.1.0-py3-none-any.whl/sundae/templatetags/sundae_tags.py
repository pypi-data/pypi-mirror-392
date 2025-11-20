from django import template
from django.urls import reverse

register = template.Library()


@register.inclusion_tag("sundae/partial/list_field.html")
def display_field(field, view):
    field_id, field, object = field
    if hasattr(view, f"display_{field_id}"):
        value = getattr(view, f"display_{field_id}")(object)
    else:
        try:
            value = field.value_to_string(object)
        except TypeError:
            value = ""
    return {"field": value}


@register.inclusion_tag("sundae/partial/list.html", takes_context=True)
def object_list(context):
    """
    Renders a list of objects with the given fields.

    Inclusion tag usage::

        {% object_list objects fields %}

    Template: ``neapolitan/partial/list.html`` — Will render a table of objects
    with links to view, edit, and delete views.
    """

    headers = [
        context["object_list"][0]._meta.get_field(f).verbose_name
        for f in context["view"].fields
    ]

    object_list = [
        {
            "instance": object,
            "fields": [
                (f, object._meta.get_field(f), object) for f in context["view"].fields
            ],
            "actions": context["view"].get_actions(object),
        }
        for object in context["object_list"]
    ]
    return {
        "bulk_editable": context["view"].bulk_edit_actions,
        "bulk_actions": context["view"].get_bulk_actions(),
        "headers": headers,
        "object_list": object_list,
        "bulk_update_proxy_url": reverse(
            f"{context['view'].model._meta.model_name}-bulk_update"
        ),
        "view": context["view"],
    }

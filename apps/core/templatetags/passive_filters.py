"""Custom template filters for Immortal Gods."""

from django import template
from django.utils.translation import gettext as _

register = template.Library()


@register.filter
def translate_passive(value):
    """Translate a passive name or description."""
    if not value:
        return value
    return _(value)

from django import template

register = template.Library()

@register.filter
def add_tailwind_classes(field, classes):
    return field.as_widget(attrs={'class': classes})
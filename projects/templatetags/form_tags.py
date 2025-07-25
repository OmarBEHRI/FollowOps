from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Ajoute une classe CSS à un champ de formulaire Django
    Usage: {{ form.field|add_class:"my-class" }}
    """
    return field.as_widget(attrs={"class": css_class})
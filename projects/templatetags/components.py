from django import template

register = template.Library()

@register.inclusion_tag('components/memberCard.html')
def member_card(name, role, tickets, photo, description, tags):
    return {
        'name': name,
        'role': role,
        'tickets': tickets,
        'photo': photo,
        'description': description,
        'tags': tags.split(',') if isinstance(tags, str) else tags
    }


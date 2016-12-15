from django import template
from bfrs.models import Bushfire

register = template.Library()

@register.assignment_tag(takes_context=True)
def has_init_authorised(context, bushfire_id):
    """
    Usage::

        {% if has_init_authorised %}
        ...
        {% endif %}

        or

        {% for bushfire in object_list %}
            {% has_init_authorised bushfire.id as init_authorised %}
            <tr>
                <td>{{ bushfire.id }}</td>
                <td><a href="{% url 'bushfire:bushfire_initial' bushfire.id %}">{{ bushfire.name }}</td>

                {% if init_authorised %}
                    <td><a href="{% url 'bushfire:bushfire_final' bushfire.id %}">{{ bushfire.name }}</td>
                {% endif %}
            </tr>
        {% endfor %}
    """

    obj = Bushfire.objects.get(id=bushfire_id)
    #import ipdb; ipdb.set_trace()
    return obj.has_init_authorised

@register.filter
def can_readonly(user):
    """
    Usage::

        {% if user|can_readonly %}
        ...
        {% endif %}
    """
    return user.groups.filter(name='ReadOnly').exists()

@register.simple_tag(takes_context=True)
def get_count(context):
    """
    Usage::
        {% get_count %}
    """
    request = context['request']
    return request.user.groups.filter(name='ReadOnly').count()

@register.simple_tag(takes_context=True)
def _can_readonly(context):
    """
    Usage::

        {% can_readonly as readonly %}
        {% if readonly %}
        ...
        {% endif %}
    """
    request = context['request']
    import ipdb; ipdb.set_trace()
    return request.user.groups.filter(name='ReadOnly').exists()


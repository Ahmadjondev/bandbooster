from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.filter(name='json_script')
def json_script(value, element_id):
    """
    Output the JSON representation of a value in a script tag.

    Usage:
    {{ my_data|json_script:"my-data" }}

    Output:
    <script id="my-data" type="application/json">{"key": "value"}</script>
    """
    if value is None:
        json_str = 'null'
    else:
        try:
            json_str = json.dumps(value)
        except TypeError:
            # Handle non-serializable objects
            if hasattr(value, 'items'):
                # Convert to dict if it has items method
                json_str = json.dumps(dict(value.items()))
            else:
                json_str = json.dumps(str(value))

    return mark_safe(f'<script id="{element_id}" type="application/json">{json_str}</script>')

@register.filter(name='to_json')
def to_json(value):
    """
    Convert a Python object to a JSON string.

    Usage:
    {{ my_data|to_json }}

    Output:
    {"key": "value"}
    """
    if value is None:
        return 'null'

    try:
        return mark_safe(json.dumps(value))
    except TypeError:
        # Handle non-serializable objects
        if hasattr(value, 'items'):
            # Convert to dict if it has items method
            return mark_safe(json.dumps(dict(value.items())))
        else:
            return mark_safe(json.dumps(str(value)))

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Get an item from a dictionary using the key.

    Usage:
    {{ my_dict|get_item:"key" }}
    """
    if not dictionary:
        return None

    return dictionary.get(key)

@register.filter(name='get_nested')
def get_nested(obj, path):
    """
    Get a nested item from an object using dot notation.

    Usage:
    {{ my_obj|get_nested:"key1.key2.key3" }}
    """
    if not obj:
        return None

    keys = path.split('.')
    result = obj

    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
        else:
            return None

        if result is None:
            return None

    return result

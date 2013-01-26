# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, unicode_literals)

from django import template
from django.core.urlresolvers import reverse
from django.template import TemplateSyntaxError, TemplateDoesNotExist
from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def mailto(value, text=''):
    """ Easily create mailto links like <a href="mailto:email"></a> """
    if not text:
        text = value
    return mark_safe("<a href=\"mailto: %s\">%s</a>" % (value, text))

@register.simple_tag(takes_context=True, name='entry')
def do_entry(context, url, title, _template="cbv_utils/menu_entry.html", args=None, **kw):
    """ returns a <li> entry for menu based on template.

    Usage:

        {% entry 'namespace:urlname' args='1,2,3' pk=1 slug='foo' title='title' }
        {% entry 'namespace:urlname' title='title' template='other/template.html' %}
    """
    if args:
        url = reverse(url, args=smart_unicode(args).translate(None, "'\"[]").split(","))
    elif kw:
        url = reverse(url, kwargs=kw)

    return template.loader.render_to_string(_template, {
        'url': url,
        'title': title,
        'active': context['request']
        })

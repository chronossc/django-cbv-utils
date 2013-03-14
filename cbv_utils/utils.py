# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, unicode_literals)

from django.utils import simplejson
from django.utils.encoding import force_unicode
from django.db.models.base import ModelBase
from django.contrib.admin.util import NestedObjects as DjangoNestedObjects


class NestedObjects(DjangoNestedObjects):

    def _nested(self, obj, seen, format_callback):
        if obj in seen:
            return []
        seen.add(obj)
        children = []
        for child in self.edges.get(obj, ()):
            children.extend(self._nested(child, seen, format_callback))
        if format_callback:
            ret = [format_callback(obj)]
        else:
            ret = [obj]
        if children:
            ret.append(children)
        return ret

    def nested(self, format_callback=None):
        """
        Return the graph as a nested list.

        """
        seen = set()
        roots = []
        for root in self.edges.get(None, ()):
            roots.extend(self._nested(root, seen, format_callback))
        return roots


class LazyJSONEncoder(simplejson.JSONEncoder):
    """ a JSONEncoder subclass that handle querysets and models objects. Add
    your code about how to handle your type of object here to use when dumping
    json """

    def default(self, o):
        # this handles querysets and other iterable types
        try:
            iterable = iter(o)
        except TypeError:
            pass
        else:
            return list(iterable)

        # this handlers Models
        try:
            isinstance(o.__class__, ModelBase)
        except Exception:
            pass
        else:
            return force_unicode(o)

        return super(LazyJSONEncoder, self).default(o)


def serialize_to_json(obj, *args, **kwargs):
    """ A wrapper for simplejson.dumps with defaults as:

    ensure_ascii=False
    cls=LazyJSONEncoder

    All arguments can be added via kwargs
    """

    kwargs['ensure_ascii'] = kwargs.get('ensure_ascii', False)
    kwargs['cls'] = kwargs.get('cls', LazyJSONEncoder)

    return simplejson.dumps(obj, *args, **kwargs)


def qdct_as_kwargs(qdct):
    kwargs = {}
    for k, v in qdct.items():
        kwargs[str(k)] = v
    return kwargs

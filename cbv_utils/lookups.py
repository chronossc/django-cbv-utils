# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, unicode_literals)

from django.db.models import Q
from operator import or_
from selectable.base import ModelLookup

EXCLUDE = (',', '.', '-', '/', ';', ':', '=', '\\',)

def search_all_terms(f):
    def wrapper(self, r, t):
        terms = [t] + \
                        [w for w in t.split() if t and t not in EXCLUDE]
        return f(self, r, terms)
    return wrapper


class BetterModelLookup(ModelLookup):

    @search_all_terms
    def get_query(self, r, terms):
        qs = self.get_queryset()
        for t in terms:
            filters = []
            for f in self.search_fields:
                filters.append(Q(**{f: t}))
            qs = qs.filter(reduce(or_, filters))
        return qs


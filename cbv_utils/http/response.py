# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, unicode_literals)
import django
from cbv_utils.utils import serialize_to_json
from django.http import HttpResponse


class JSONResponse(HttpResponse):
    """ JSON response class """
    def __init__(self, content='', json_opts={}, *a, **kw):
        """
        This returns a object that we send as json content using
        utils.serialize_to_json, that is a wrapper to simplejson.dumps
        method using a custom class to handle models and querysets. Put your
        options to serialize_to_json in json_opts, other options are used by
        response.
        """
        if content:
            content = serialize_to_json(content, **json_opts)
        else:
            content = serialize_to_json([], **json_opts)

        # Assert application type is JSON. In Django < 1.5.0 argument was
        # mimetype, after 1.5.0 it is content_type.
        if django.VERSION[:3] < (1, 5, 0):
            kw.update({'mimetype': 'application/json'})
        else:
            kw.update({'content_type': 'application/json'}),
        super(JSONResponse, self).__init__(content, *a, **kw)

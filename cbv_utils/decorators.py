# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, unicode_literals)

""" There is decorators for CBV that mimics Django default decorators.

    This decorators just send args to real decorators and attach it to
    View.dispatch method.

    Code here is based on http://stackoverflow.com/questions/6069070/how-to-use-permission-required-decorators-on-django-class-based-views

    """

from django.contrib.auth.decorators import (login_required, permission_required,
    user_passes_test)
from django.utils.decorators import method_decorator


def class_user_passes_test(ftest):
    ''' Apply @user_passes_test decorator.
        https://docs.djangoproject.com/en/1.5/topics/auth/default/#limiting-access-to-logged-in-users-that-pass-a-test
    '''
    def simple_decorator(View):
        View.dispatch = method_decorator(user_passes_test(ftest))(View.dispatch)
        return View

    return simple_decorator


def class_login_required():
    ''' Apply @login_required decorator.
        https://docs.djangoproject.com/en/1.5/topics/auth/default/#the-login-required-decorator
    '''
    def simple_decorator(View):
        View.dispatch = method_decorator(login_required)(View.dispatch)
        return View

    return simple_decorator


def class_permission_required(perm):
    ''' Apply @permission_required decorator.
        https://docs.djangoproject.com/en/1.5/topics/auth/default/#the-permission-required-decorator
    '''
    def simple_decorator(View):
        View.dispatch = method_decorator(permission_required(perm))(View.dispatch)
        return View
    return simple_decorator

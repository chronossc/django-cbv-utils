# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, unicode_literals)

from django.views import generic
from django.core.urlresolvers import resolve
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.template import RequestContext
from django.template.loader import render_to_string
from cbv_utils.http.response import JSONResponse


class CBVUtilsMixin(object):

    base_template = ''

    def _make_magic(self):
        self.model_opts = self.model._meta
        try:
            self.mod_name = self.mod_name
        except (AttributeError, KeyError):
            try:
                self.mod_name = settings.CBV_APP_LABELS[self.model_opts.app_label]
            except (AttributeError, KeyError):
                self.mod_name = self.model_opts.app_label

    def get(self, *a, **kw):
        self._make_magic()
        r = super(CBVUtilsMixin, self).get(*a, **kw)
        return r

    def post(self, *a, **kw):
        self._make_magic()
        r = super(CBVUtilsMixin, self).post(*a, **kw)
        return r

    def get_context_data(self, **kw):
        context = super(CBVUtilsMixin, self).get_context_data(**kw)
        self.url_info = resolve(self.request.path)
        if self.url_info.namespace:
            namespace_str = self.url_info.namespace + ':'
        else:
            namespace_str = ''

        url_model_name = self.url_info.url_name.split('_')[0]

        context.update({
            'mod_name': self.mod_name,
            'verbose_name': getattr(self, 'verbose_name', self.model_opts.verbose_name),
            'verbose_name_plural': getattr(self, 'verbose_name_plural', self.model_opts.verbose_name_plural),
            'long_desc': getattr(self, 'long_desc', ''),
            'base_template': self.base_template or self.model_opts.app_label + '/base.html',
        })
        if self.template_name_suffix == '_list':
            context.update({
            'object_list_template': self.model_opts.app_label + '/' + self.model_opts.module_name + self.template_name_suffix + '_page.html',
            'add_item_url': namespace_str + url_model_name + '_new',
            })
        else:
            context.update({
                'object_list_url': namespace_str + url_model_name + '_list',
            })

        if self.template_name_suffix == '_form':
            context.update({
                'delete_url': namespace_str + url_model_name + '_delete'
            })
        return context


class SuccessMsgMixing(object):

    def form_valid(self, *a, **kw):
        r = super(SuccessMsgMixing, self).form_valid(*a, **kw)
        try:
            self.send_success_msg()
        except:
            print "Failed send_success_msg on %s obj %s" % (self, self.object)
        return r


class ListView(CBVUtilsMixin, generic.ListView):

    long_desc = ''

    def get_context_data(self, **kw):
        context = super(ListView, self).get_context_data(**kw)
        context['is_list'] = True
        context['long_desc'] = self.long_desc
        return context


class CreateView(SuccessMsgMixing, CBVUtilsMixin, generic.CreateView):

    long_desc = ''

    def get_context_data(self, **kw):
        context = super(CreateView, self).get_context_data(**kw)
        context['is_create'] = True
        context['long_desc'] = self.long_desc
        return context

    def send_success_msg(self):
        msg = "O(a) %s %s foi criado(a) com sucesso." % (
            self.object._meta.verbose_name, self.object)
        return messages.success(self.request, msg)


class UpdateView(SuccessMsgMixing, CBVUtilsMixin, generic.UpdateView):

    long_desc = ''

    def get_context_data(self, **kw):
        context = super(UpdateView, self).get_context_data(**kw)
        context['is_update'] = True
        context['long_desc'] = self.long_desc
        return context

    def send_success_msg(self):
        msg = "O(a) %s %s foi atualizado(a) com sucesso." % (
            self.get_object()._meta.verbose_name, self.get_object())
        return messages.success(self.request, msg)


class DeleteView(CBVUtilsMixin, generic.DeleteView):

    long_desc = ''

    def delete(self, request, *a, **kw):
        r = super(DeleteView, self).delete(request, *a, **kw)
        try:
            self.send_success_msg()
        except:
            print "Failed send_success_msg on %s obj %s" % (self, self.object)
        return r

    def send_success_msg(self):
        msg = "O(a) %s %s foi excluído(a) com sucesso." % (
            self.object._meta.verbose_name,
            self.object)
        return messages.success(self.request, msg)

    def get_context_data(self, **kw):
        context = super(DeleteView, self).get_context_data(**kw)
        context['is_delete'] = True
        context['long_desc'] = self.long_desc
        return context


class AjaxUpdateView(generic.UpdateView):

    http_method_names = ['post', 'put']
    template_name_suffix = '_ajax_form'

    def form_valid(self, form):
        self.object = form.save()
        return JSONResponse({'status': 'success', 'msg': self.send_success_msg(),
            'form': self.render_form(form, success=self.send_success_msg())})

    def form_invalid(self, form):
        return JSONResponse({'status': 'error', 'errors': form.errors,
            'form': self.render_form(form)})

    def post(self, request, *a, **kw):
        if request.is_ajax():
            self.object = self.get_object()
            form = self.get_form(self.get_form_class())
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        else:
            return HttpResponseForbidden("403: Access denied. This url should be acessed via Ajax requests.")

    def render_form(self, form, **context):
        return render_to_string(self.get_template_names(),
            self.get_context_data(form=form, **context), RequestContext(self.request))

    def send_success_msg(self):
        # Please, customize this method in your view
        return "It's saved"

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from auth_app.forms import  ChangePasswordForm

from auth_app.models import kozUser

class ClientDashboardView(LoginRequiredMixin, TemplateView):
   
   template_name = "clients_templates/client.html"
   
   def get_context_data(self, **kwargs):
      context =  super().get_context_data(**kwargs)
      context["client"] = self.request.user
      context["commercial"] = self.request.user.assigned_commercial
      if 'change_pass_form' not in context:
         context["change_pass_form"] = ChangePasswordForm()
      return context


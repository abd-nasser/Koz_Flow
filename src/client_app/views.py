from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.contrib import messages
from django.views.generic import TemplateView, DetailView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


from auth_app.forms import  ChangePasswordForm
from .models import Documents
from auth_app.models import kozUser

from leads_app.models import demande_financement

class ClientDashboardView(LoginRequiredMixin, TemplateView):
   
   template_name = "clients_templates/client.html"
   
   def get_context_data(self, **kwargs):
      context =  super().get_context_data(**kwargs)
      context["client"] = self.request.user
      context["commercial"] = self.request.user.assigned_commercial
      if 'change_pass_form' not in context:
         context["change_pass_form"] = ChangePasswordForm()
      return context


class ClientDetailView(LoginRequiredMixin, DetailView):
   model = kozUser
   template_name = "clients_templates/client_detail.html"
   context_object_name = "client"


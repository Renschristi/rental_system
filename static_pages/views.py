"""
Static Pages Views (Terms, About, Contact)
"""
from django.views.generic import TemplateView


class TermsView(TemplateView):
    """Terms & Conditions page"""
    template_name = 'static_pages/terms.html'


class AboutView(TemplateView):
    """About Us page"""
    template_name = 'static_pages/about.html'


class ContactView(TemplateView):
    """Contact Us page"""
    template_name = 'static_pages/contact.html'

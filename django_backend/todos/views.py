from django.views.generic import TemplateView


class DashboardView(TemplateView):
    """
    A dashboard view for the test application.
    """
    template_name = 'todos/index.html'

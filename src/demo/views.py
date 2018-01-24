from __future__ import unicode_literals

from django.db.models import Prefetch
from django.views import generic

from demo.models import ServiceCategory
from waves.wcore.models import get_service_model
from waves.wcore.views.services import ServiceDetailView as CoreDetailView

Service = get_service_model()


class ServiceDetailView(CoreDetailView):
    model = Service
    template_name = 'demo/service_details.html'

    def render_to_response(self, context, **response_kwargs):
        response = super(ServiceDetailView, self).render_to_response(context, **response_kwargs)
        response.set_cookie('waves_token', 'd8ecf156906d846c799a4cb467fcbdf56abe0f11')
        return response


# Create your views here.
class CategoryDetailView(generic.DetailView):
    context_object_name = 'category'
    model = ServiceCategory
    template_name = 'category/category_details.html'
    context_object_name = 'category'

    def get_queryset(self):
        return ServiceCategory.objects.all().prefetch_related(
            Prefetch('category_tools',
                     queryset=Service.objects.get_services(user=self.request.user),
                     to_attr="category_public_tools"
                     )
        )


class CategoryListView(generic.ListView):
    template_name = "category/categories_list.html"
    model = ServiceCategory
    context_object_name = 'online_categories'

    def get_queryset(self):
        return ServiceCategory.objects.all().prefetch_related(
            Prefetch('category_tools',
                     queryset=Service.objects.get_services(user=self.request.user),
                     to_attr="category_public_tools"
                     )
        )

from django.http import JsonResponse
from django.utils.cache import add_never_cache_headers
from django.views import View
from wagtail_personalisation.adapters import get_segment_adapter


class ElectSegmentView(View):
    def post(self, request, *args, **kwargs):
        adapter = get_segment_adapter(request)
        adapter.refresh()
        response = JsonResponse({
            'segments': list(map(lambda s: s.id, adapter.get_segments()))
        })
        add_never_cache_headers(response)
        return response

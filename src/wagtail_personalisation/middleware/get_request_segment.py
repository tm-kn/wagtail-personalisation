from wagtail_personalisation.adapters import get_segment_adapter
from wagtail_personalisation.models import Segment


class GetRequestSegmentMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        adapter = get_segment_adapter(request)
        setattr(request, '_skip_segmenting_user', True)
        segment_ids = []
        for s in request.GET.get('wagtail-segments','').split(','):
            try:
                segment_ids.append(int(s))
            except (ValueError, TypeError):
                pass
        segments = Segment.objects.enabled().filter(pk__in=segment_ids)
        adapter.set_segments(segments)
        return self.get_response(request)

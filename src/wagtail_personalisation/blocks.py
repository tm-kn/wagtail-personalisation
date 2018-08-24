from __future__ import absolute_import, unicode_literals

from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from django.utils.translation import ugettext_lazy as _
from wagtail.core import blocks

from wagtail_personalisation.adapters import get_segment_adapter
from wagtail_personalisation.models import Segment


def list_segment_choices():
    yield -1, ("Show to everyone")
    for pk, name in Segment.objects.values_list('pk', 'name'):
        yield pk, name


class PersonalisedStructBlock(blocks.StructBlock):
    """Struct block that allows personalisation per block."""
    segments = blocks.ListBlock(blocks.ChoiceBlock(
        choices=list_segment_choices,
        required=False, label=_("Personalisation segment"),
        help_text=_("Only show this content block for users in this segment"))
    )

    def clean(self, value):
        cleaned_data = super().clean(value)
        segments = cleaned_data['segments']
        for segment_id in segments:
            segment_id = int(segment_id)
            if segment_id == -1 and len(segments) > 1:
                raise ValidationError(
                    'ValidationError in PersonalisedStructBlock',
                    params={
                        'segments': ErrorList([
                            ValidationError('ValidationError in ListBlock',
                            params=ErrorList([
                                ValidationError('test')
                                for i in range(len(segments))
                                if i == 0 else None
                            ])

                        )])
                    }
                )
        return cleaned_data

    def render(self, value, context=None):
        """Only render this content block for users in this segment.

        :param value: The value from the block
        :type value: dict
        :param context: The context containing the request
        :type context: dict
        :returns: The provided block if matched, otherwise an empty string
        :rtype: blocks.StructBlock or empty str

        """
        request = context['request']
        adapter = get_segment_adapter(request)
        user_segments = adapter.get_segments()
        segment_ids = []
        for segment in value['segments']:
            try:
                segment_ids.append(int(segment))
            except (TypeError, ValueError):
                continue

        if not segment_ids:
            return ''

        if -1 in segment_ids:
            return super(PersonalisedStructBlock, self).render(
                value, context)

        for segment in user_segments:
            if segment.id in segment_ids:
                return super(PersonalisedStructBlock, self).render(
                    value, context)

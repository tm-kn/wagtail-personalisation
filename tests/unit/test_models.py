from __future__ import absolute_import, unicode_literals

import datetime

import pytest
from django.db.models import ProtectedError

from tests.factories.page import ContentPageFactory
from tests.factories.segment import SegmentFactory
from tests.site.pages import models
from wagtail_personalisation.models import PersonalisablePageMetadata
from wagtail_personalisation.rules import TimeRule


@pytest.mark.django_db
def test_segment_create():
    segment = SegmentFactory()
    TimeRule(
        start_time=datetime.time(8, 0, 0),
        end_time=datetime.time(23, 0, 0),
        segment=segment)


@pytest.mark.django_db
def test_metadata_page_has_variants(segmented_page):
    assert not segmented_page.personalisation_metadata.is_canonical
    assert not segmented_page.personalisation_metadata.has_variants

    canonical = segmented_page.personalisation_metadata.canonical_page
    assert canonical.personalisation_metadata.is_canonical
    assert canonical.personalisation_metadata.has_variants


@pytest.mark.django_db
def test_content_page_model():
    page = ContentPageFactory()
    qs = models.ContentPage.objects.all()
    assert page in qs


@pytest.mark.django_db
def test_variant_can_be_deleted_without_error(segmented_page):
    segmented_page.delete()
    # Make sure the metadata gets deleted because of models.CASCADE.
    with pytest.raises(PersonalisablePageMetadata.DoesNotExist):
        segmented_page._personalisable_page_metadata.refresh_from_db()


@pytest.mark.django_db
def test_canonical_page_deletion_is_protected(segmented_page):
    # When deleting canonical page without deleting variants, it should return
    # an error. All variants should be deleted beforehand.
    with pytest.raises(ProtectedError):
        segmented_page.personalisation_metadata.canonical_page.delete()


@pytest.mark.django_db
def test_page_protection_when_deleting_segment(segmented_page):
    segment = segmented_page.personalisation_metadata.segment
    assert len(segment.get_used_pages())
    with pytest.raises(ProtectedError):
        segment.delete()

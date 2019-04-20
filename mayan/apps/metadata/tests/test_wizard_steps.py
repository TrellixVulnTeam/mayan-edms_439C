from __future__ import unicode_literals

from furl import furl

from django.urls import reverse

from mayan.apps.documents.models import Document
from mayan.apps.documents.permissions import permission_document_create
from mayan.apps.documents.tests import (
    GenericDocumentViewTestCase, TEST_SMALL_DOCUMENT_PATH,
)
from mayan.apps.sources.models import WebFormSource
from mayan.apps.sources.tests.literals import (
    TEST_SOURCE_LABEL, TEST_SOURCE_UNCOMPRESS_N,
)

from .literals import (
    TEST_METADATA_VALUE_UNICODE, TEST_METADATA_VALUE_WITH_AMPERSAND
)
from .mixins import MetadataTypeTestMixin


class DocumentUploadMetadataTestCase(MetadataTypeTestMixin, GenericDocumentViewTestCase):
    def setUp(self):
        super(DocumentUploadMetadataTestCase, self).setUp()
        self.login_user()
        self.source = WebFormSource.objects.create(
            enabled=True, label=TEST_SOURCE_LABEL,
            uncompress=TEST_SOURCE_UNCOMPRESS_N
        )

        self.test_document.delete()

        self.test_document_type.metadata.create(
            metadata_type=self.metadata_type, required=True
        )

    def test_upload_interactive_with_unicode_metadata(self):
        url = furl(reverse('sources:upload_interactive'))
        url.args['metadata0_id'] = self.metadata_type.pk
        url.args['metadata0_value'] = TEST_METADATA_VALUE_UNICODE

        self.grant_access(
            permission=permission_document_create, obj=self.test_document_type
        )

        # Upload the test document
        with open(TEST_SMALL_DOCUMENT_PATH, mode='rb') as file_descriptor:
            response = self.post(
                path=url, data={
                    'document-language': 'eng', 'source-file': file_descriptor,
                    'document_type_id': self.test_document_type.pk,
                }
            )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(
            Document.objects.first().metadata.first().value,
            TEST_METADATA_VALUE_UNICODE
        )

    def test_upload_interactive_with_ampersand_metadata(self):
        url = furl(reverse('sources:upload_interactive'))
        url.args['metadata0_id'] = self.metadata_type.pk
        url.args['metadata0_value'] = TEST_METADATA_VALUE_WITH_AMPERSAND

        self.grant_access(
            permission=permission_document_create, obj=self.test_document_type
        )
        # Upload the test document
        with open(TEST_SMALL_DOCUMENT_PATH, mode='rb') as file_descriptor:
            response = self.post(
                path=url, data={
                    'document-language': 'eng', 'source-file': file_descriptor,
                    'document_type_id': self.test_document_type.pk,
                }
            )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(
            Document.objects.first().metadata.first().value,
            TEST_METADATA_VALUE_WITH_AMPERSAND
        )

    def test_initial_step_conditions(self):
        self.grant_access(
            obj=self.test_document_type, permission=permission_document_create
        )

        response = self.post(
            viewname='sources:document_create_multiple', data={
                'document_type_selection-document_type': self.test_document_type.pk,
                'document_create_wizard-current_step': 0
            }
        )

        self.assertContains(response=response, text='Step 2', status_code=200)

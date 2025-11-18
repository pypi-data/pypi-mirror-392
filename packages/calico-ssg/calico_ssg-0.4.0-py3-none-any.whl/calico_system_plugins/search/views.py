import re

from django.http import JsonResponse
from django.utils.html import strip_tags
from django.views.generic import View

from calico.models import Page
from calico.templatetags.calico import md_include
from calico.utils import calico_setting


class SearchIndexView(View):
    """Class-based view to generate and return a search index for client-side search."""

    def process_text(self, text):
        """
        Process text by rendering markdown, stripping HTML, and normalizing whitespace.

        Args:
            text: A string of markdown content to process

        Returns:
            str: The processed plain text suitable for search indexing
        """
        if not text:
            return ""

        # Use md_include to render markdown to HTML with templating
        rendered_content = md_include(text)

        # Strip HTML tags to get plain text for better search results
        plain_text = strip_tags(rendered_content)

        # Normalize all whitespace characters (spaces, tabs, newlines, etc.)
        plain_text = re.sub(r'[\s\t\n\r]+', ' ', plain_text).strip()

        return plain_text

    def create_documents(self, exclude_patterns):
        """
        Create a list of documents for the search index.

        Args:
            exclude_patterns: List of patterns to exclude from indexing

        Returns:
            list: List of document dictionaries for the search index
        """
        documents = []

        # Get all pages
        pages = Page.pages_in_dir(recursive=True)

        for page in pages:
            # Skip excluded pages
            if any(pattern in page.url for pattern in exclude_patterns):
                continue

            # Start with basic document fields
            doc = {
                'id': page.slug,
                'url': page.url,
                'title': page.meta.get('title', ''),
                'content': self.process_text(page.md_content),
            }

            # Add excerpt if available
            if 'excerpt' in page.meta.data:
                doc['excerpt'] = self.process_text(page.meta.get('excerpt'))

            # Add tags if available (tags are always a list)
            if 'tags' in page.meta.data:
                doc['tags'] = ' '.join(page.meta.get('tags'))

            # Include any additional metadata fields defined in SEARCH_FIELDS
            search_fields = calico_setting('SEARCH_FIELDS')
            for field in search_fields:
                if field not in doc and field in page.meta.data:
                    doc[field] = page.meta.get(field)

            documents.append(doc)

        return documents

    def create_schema(self):
        """
        Create the schema for the Lunr.js search index.

        Returns:
            dict: Schema configuration for Lunr.js
        """
        search_fields = calico_setting('SEARCH_FIELDS')
        search_ref_field = calico_setting('SEARCH_REF_FIELD')
        search_boost = calico_setting('SEARCH_BOOST')

        return {
            'fields': search_fields,
            'ref': search_ref_field,
            'boost': search_boost,
        }

    def get(self, request, *args, **kwargs):
        """Handle GET requests to return the search index."""
        # Get exclude patterns from settings
        exclude_patterns = calico_setting('SEARCH_EXCLUDE_PATTERNS')

        # Create documents and schema for the index
        documents = self.create_documents(exclude_patterns)
        schema = self.create_schema()

        # Create index data
        index_data = {
            'schema': schema,
            'documents': documents,
        }

        return JsonResponse(index_data)

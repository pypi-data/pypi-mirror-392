# Calico Search Plugin

This plugin adds client-side search functionality to Calico static sites using Lunr.js.

## Features

- Provides search index as a dynamic endpoint and static asset
- Client-side search using Lunr.js
- Customizable search fields and weighting
- Easily integrated with any Calico theme

## Usage

1. Make sure the plugin is installed (it's included with Calico but disabled by default)

2. Enable the plugin by removing it from the `exclude_plugins` list in your website.py file:

```python
app = Calico(
    # Remove search from exclude_plugins if it's there
    exclude_plugins=[]  # or omit this line completely
)
```

3. Add the search widget to your template:

```html
{% component 'search' %}
```

The search index will be automatically generated during development and site builds at the URL `/calico-lunr.json`.

## Configuration

The following settings can be customized in your website.py file:

```python
app = Calico(
    # Other settings...
    SEARCH_EXCLUDE_PATTERNS=['/excluded-path/'],
    SEARCH_FIELDS=['title', 'content'],
    SEARCH_REF_FIELD='url',
    SEARCH_BOOST={
        'title': 10,
        'content': 1
    }
)
```

## How It Works

1. The search index is dynamically generated and served at `/calico-lunr.json`
2. During static builds, this index is included in the output files
3. The client-side JavaScript loads this index when needed
4. User searches are processed entirely on the client side

## Requirements

- lunr (Python library for generating the search index)
- Lunr.js (included in the plugin's static files)
# django-toon-rest

Django REST Framework library for rendering responses in TOON format (Token-Oriented Object Notation).

## Description

`django-toon-rest` provides a custom renderer for Django REST Framework that allows returning API responses in TOON format, a lightweight and LLM-friendly format.

## Installation

```bash
pip install django-toon-rest
```

This will automatically install required dependencies like `json-toon` and `djangorestframework`.

## Usage

### Basic Configuration

```python
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer
from django_toon_rest.renderers import TOONRenderer

class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    renderer_classes = [JSONRenderer, TOONRenderer]
    
    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)
```

### Content Negotiation

The client must send the `Accept: application/toon` header to receive the response in TOON format:

```bash
curl -H "Accept: application/toon" http://api.example.com/items/
```

## Features

- ✅ Custom renderer compatible with DRF
- ✅ Automatic content negotiation
- ✅ Automatic conversion of Python data to TOON
- ✅ Compatible with all DRF data structures
- ✅ Automatic handling of Django Decimal fields

## Data Type Handling

The `TOONRenderer` automatically handles common Django/DRF data types:

- **Decimal fields**: Automatically converted to `float` for JSON serialization
- **Nested objects**: Preserved as JSON within table cells (TOON format behavior)
- **Lists and dictionaries**: Fully supported with proper formatting

This means you don't need to modify your serializers - the renderer handles type conversions automatically.

## Example Project

For a complete working example with models, serializers, and sample data, see the example project:

- **Repository**: [django-toon-rest-example](https://github.com/martinartaza/django-toon-rest-example) (coming soon)

The example project demonstrates:
- Models with relationships (ForeignKey, ManyToMany)
- Nested serializers
- Multiple endpoints with TOON rendering
- Sample data fixtures

## Dependencies

- Python >= 3.8
- Django REST Framework >= 3.0.0 (installed automatically)
- json-toon >= 1.0.0 (installed automatically)

## Development

```bash
# Clone the repository
git clone https://github.com/martinartaza/django-toon-rest.git
cd django-toon-rest

# Install in development mode
pip install -e .
```

## Testing

```bash
# Optional: dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest -q
```

Expected output (example):

```
4 passed in 0.XXs
```

## License

MIT License

## Author

Martin Artaza

## Repository

https://github.com/martinartaza/django-toon-rest

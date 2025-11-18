# Djvurn Rbac

> RBAC with teams and DRF integration

[![PyPI version](https://badge.fury.io/py/djvurn-rbac.svg)](https://badge.fury.io/py/djvurn-rbac)
[![Python Support](https://img.shields.io/pypi/pyversions/djvurn-rbac.svg)](https://pypi.org/project/djvurn-rbac/)
[![Django Support](https://img.shields.io/badge/django-5.0+-blue.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Part of the [djvurn package ecosystem](https://github.com/hmesfin/djvurn-packages).

## Features

- 🎯 **DRF-first** - Complete REST API with ViewSets and serializers
- 🔐 **JWT authentication** - Works seamlessly with `djangorestframework-simplejwt`
- 📘 **TypeScript support** - Full type definitions (separate npm package)
- 🎨 **Vue components** - Ready-to-use UI components (separate npm package)
- 🧪 **Well-tested** - 90%+ test coverage
- 📚 **Documented** - Comprehensive guides and API reference

## What This Wraps

This package wraps [`django-guardian`](https://pypi.org/project/django-guardian/) with:

- DRF serializers, ViewSets, and permissions
- JWT authentication integration
- OpenAPI/Swagger schema generation
- Team/organization support
- Real-time updates (WebSocket)

If you're using the vanilla `django-guardian`, see the [Migration Guide](#migration-from-vanilla-package).

## Installation

```bash
pip install djvurn-rbac
```

Or with Poetry:

```bash
poetry add djvurn-rbac
```

## Quick Start

### 1. Add to INSTALLED_APPS

```python
# settings.py
INSTALLED_APPS = [
    # Django apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    # ...

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'django_guardian',  # Base package

    # djvurn packages
    'djvurn_rbac',  # This package
]
```

### 2. Configure REST Framework

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.CursorPagination',
    'PAGE_SIZE': 20,
}
```

### 3. Add URLs

```python
# urls.py
from django.urls import path, include
from djvurn_rbac.api import router

urlpatterns = [
    path('api/', include(router.urls)),
    # ... other URLs
]
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Start Using the API

```python
# In your code
from djvurn_rbac import [TODO: Add usage example]

# Or via the API
# GET /api/[resource]/
# POST /api/[resource]/
```

## API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/[resource]/` | List resources |
| POST | `/api/[resource]/` | Create resource |
| GET | `/api/[resource]/{id}/` | Retrieve resource |
| PUT | `/api/[resource]/{id}/` | Update resource |
| PATCH | `/api/[resource]/{id}/` | Partial update |
| DELETE | `/api/[resource]/{id}/` | Delete resource |

### Example Requests

**List Resources**

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/[resource]/
```

**Create Resource**

```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"field": "value"}' \
     http://localhost:8000/api/[resource]/
```

For full API documentation, see [API Reference](docs/api-reference.md).

## Frontend Integration

### TypeScript/JavaScript

Install the TypeScript package:

```bash
npm install @djvurn/rbac
```

Usage:

```typescript
import { useResource } from '@djvurn/rbac'

const client = useResource({
  baseURL: 'http://localhost:8000/api',
  token: 'YOUR_JWT_TOKEN'
})

const items = await client.list()
```

### Vue 3

```vue
<script setup lang="ts">
import { useResource } from '@djvurn/rbac'

const { items, loading, error, refresh } = useResource()
</script>

<template>
  <div v-if="loading">Loading...</div>
  <div v-else-if="error">Error: {{ error }}</div>
  <div v-else>
    <div v-for="item in items" :key="item.id">
      {{ item.name }}
    </div>
  </div>
</template>
```

## Configuration

### Settings

```python
# settings.py

# Djvurn Rbac settings
DJVURN_RBAC = {
    # Add any package-specific settings here
}
```

## Migration from Vanilla Package

If you're currently using `django-guardian`:

1. **Install this package** alongside the base package
2. **Add to INSTALLED_APPS** (keep both packages)
3. **Run migrations** - No data migration needed
4. **Update your views** to use DRF ViewSets
5. **Update your frontend** to use the REST API

See [Migration Guide](docs/migration.md) for detailed steps.

## Development

### Setup

```bash
# Clone the mono-repo
git clone https://github.com/hmesfin/djvurn-packages.git
cd djvurn-packages/packages/djvurn-rbac

# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov
```

### Running Tests

```bash
# All tests
poetry run pytest

# Specific test file
poetry run pytest tests/test_models.py

# With coverage report
poetry run pytest --cov --cov-report=html
open htmlcov/index.html
```

### Code Quality

```bash
# Format code
poetry run black src/ tests/
poetry run ruff check --fix src/ tests/

# Type checking
poetry run mypy src/
```

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits

- Built on top of [`django-guardian`](https://pypi.org/project/django-guardian/)
- Part of the [djvurn package ecosystem](https://github.com/hmesfin/djvurn-packages)
- Created by [Gojjo Tech](https://github.com/hmesfin)

## Support

- **Documentation**: [Read the docs](https://djvurn-rbac.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/hmesfin/djvurn-packages/issues)
- **Discussions**: [GitHub Discussions](https://github.com/hmesfin/djvurn-packages/discussions)

# Python (PyPI) Repository Support

## Requirement
Support querying Python package repositories in Nexus.

## Key Operations
1. **Search Python packages** by name or keyword
2. **List versions** of a package
3. **Get package metadata** (description, author, latest version)
4. **Download URLs** for wheels and source distributions

## API Endpoints
- `GET /service/rest/v1/search?repository=<repo>&format=pypi&name=<package>`
- PyPI JSON API endpoints if proxied through Nexus

## Success Criteria
- Can search PyPI-hosted and PyPI-proxy repositories
- Returns package name, version, format (wheel, sdist)
- Handles Python package naming conventions (underscores vs hyphens)

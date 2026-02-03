# Docker Registry Support

## Requirement
Support querying Docker registries in Nexus.

## Key Operations
1. **List Docker repositories** (image names)
2. **List tags** for a specific image
3. **Get image metadata** (digest, size, layers, created date)
4. **Search images** by name or label

## API Endpoints
- `GET /service/rest/v1/search?repository=<repo>&format=docker`
- Docker Registry v2 API via Nexus proxy
- `GET /v2/<image>/tags/list`

## Success Criteria
- Can list all Docker images in a repository
- Returns tags with metadata (digest, size, push date)
- Handles multi-architecture images
- Supports both hosted and proxy Docker repositories

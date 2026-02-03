# Maven Repository Support

## Requirement
Support querying Maven repositories in Nexus for components and versions.

## Key Operations
1. **Search Maven artifacts** by groupId, artifactId, or coordinates
2. **List versions** of a specific artifact
3. **Get artifact metadata** (POM details, dependencies, latest version)
4. **Download URLs** for artifacts (JAR, sources, javadoc)

## API Endpoints (Nexus REST API v1)
- `GET /service/rest/v1/search?repository=<repo>&group=<groupId>&name=<artifactId>`
- `GET /service/rest/v1/components?repository=<repo>`

## Success Criteria
- Can search across all Maven repositories or specific ones
- Returns structured data (groupId, artifactId, version, format)
- Handles multi-repository results
- Supports pagination for large result sets

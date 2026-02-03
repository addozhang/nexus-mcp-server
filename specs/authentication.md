# Authentication Spec

## Requirement
The MCP server must accept Nexus connection credentials via request headers, not hardcoded configuration.

## Headers
- `X-Nexus-Url`: Base URL of Nexus instance (e.g., `https://nexus.company.com`)
- `X-Nexus-Username`: Username for authentication
- `X-Nexus-Password`: Password for authentication

## Security Considerations
- Credentials are per-request, not stored
- Support both HTTP Basic Auth and token-based auth to Nexus API
- Validate URL format before making requests
- Handle authentication failures gracefully

## Success Criteria
- MCP server can connect to any Nexus instance using provided headers
- Clear error messages for missing/invalid credentials
- No credentials hardcoded or logged

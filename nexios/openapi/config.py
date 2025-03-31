from .models import Contact, License, Server, OpenAPI, Info, SecurityScheme, Components
from typing import Dict, List, Optional


class OpenAPIConfig:
    def __init__(
        self,
        title: str = "API Documentation",
        version: str = "1.0.0",
        description: str = "",
        servers: Optional[List[Server]] = None,
        contact: Optional[Contact] = None,
        license: Optional[License] = None,
    ):
        self.openapi_spec = OpenAPI(
            openapi="3.0.0",
            info=Info(
                title=title,
                version=version,
                description=description,
                contact=contact,
                license=license,
            ),
            paths={},
            servers=servers or [Server(url="/")],
            components=Components(),
        )
        self.security_schemes: Dict[str, SecurityScheme] = {}

    def add_security_scheme(self, name: str, scheme: SecurityScheme):
        """Add a security scheme to the OpenAPI specification"""
        if not self.openapi_spec.components:
            self.openapi_spec.components = Components()

        if not self.openapi_spec.components.securitySchemes:
            self.openapi_spec.components.securitySchemes = {}

        self.openapi_spec.components.securitySchemes[name] = scheme

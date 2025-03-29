def generate_swagger_ui(title, 
                        css = "https://unpkg.com/swagger-ui-dist@4.18.3/swagger-ui.css",
                        js="https://unpkg.com/swagger-ui-dist@4/swagger-ui-bundle.js",
                        openapi_url = "/openapi.json") -> str:
        """Generate Swagger UI HTML"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title} - Docs</title>
            <link rel="stylesheet" href={css}>
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src={js}></script>
            <script>
                window.onload = function() {{
                    SwaggerUIBundle({{
                        url: {openapi_url},
                        dom_id: '#swagger-ui',
                        presets: [
                            SwaggerUIBundle.presets.apis,
                            SwaggerUIBundle.SwaggerUIStandalonePreset
                        ],
                        layout: "BaseLayout"
                    }});
                }}
            </script>
        </body>
        </html>
        """
## v2.10.3 (2025-08-28)

### Feat

- **application**: add global state support
- **websocket**: enhance websocket route addition and update docs

### Fix

- **docs**: correct logging_middleware function parameters

## v2.10.2 (2025-08-16)

### Fix

- **auth**: add Callable import to jwt backend
- **request**: review request.json

## v2.10.1 (2025-08-07)

### Fix

- **csrf**: improve CSRF protection and token handling
- **docs**: fix routing docs orgnization
- **docs**: fix websockets documentation on channels

## v2.10.0 (2025-08-02)

### Feat

- **auth**: introduce new has_permission decorator
- **config**: allow set_config to auto initalize MakeConfig class when kwargs is passed in

### Fix

- **docs**: fix issues in docs
- **di**: fix context initalization in all middleware instaces

## v2.9.3 (2025-07-30)

### Fix

- **multipart**: Fix multipart form data support

### Refactor

- **deps**: clean dependecy
- **docs**: refactor auth docs

## v2.9.2 (2025-07-28)

### Feat

- **middleware**: enhance CSRF protection and documentation

## v2.9.1 (2025-07-27)

### Fix

- clean up formatting in index.md and remove unnecessary whitespace
- remove duplicate entry for granian in requirements.txt

## v2.9.0 (2025-07-23)

### Feat

- update global dependency test to use custom error handling
- update README and main application structure, remove unused files, and add new index template
- add support for dependency injection error handling and global dependencies in tests
- enhance inject_dependencies to support context and app dependency injection
- enhance Context initialization with additional parameters for improved middleware functionality

### Fix

- ensure proper handling of async and sync handlers in inject_dependencies function
- update user type annotation from User to BaseUser in Context class

### Refactor

- simplify dependency injection in Router class

## v2.8.6 (2025-07-19)

## v2.8.5 (2025-07-19)

## v2.8.4 (2025-07-18)

### Fix

- improve CSRF token handling and enhance security middleware defaults

## v2.8.3 (2025-07-18)

### Fix

- initialize \_session_cache in BaseSessionInterface constructor

## v2.8.2 (2025-07-18)

### Feat

- add virtualenv setup step in release workflow
- implement new tag creation workflow for releases
- implement new tag creation workflow for releases

### Fix

- update build command in release workflow

### Refactor

- simplify release workflow by removing deprecated steps

## v2.8.0 (2025-07-16)

### Feat

- enhance dependency injection documentation
- add support for app-level and router-level dependencies
- add support for synchronous and asynchronous generator dependencies
- enhance run command to support custom commands as lists or strings

### Fix

- update release and triage workflows for consistency
- resolve issues with dependency merging in Router class
- add TYPE_CHECKING import for improved type hinting in \_builder.py

## v2.7.0 (2025-07-09)

### Feat

- enhance templating system with request context support

### Fix

- improve session handling and error logging
- add version bump test comment to main module

## v2.6.2 (2025-07-05)

### Refactor

- simplify app.run() method and add development warning

## v2.6.2a1 (2025-07-04)

### Refactor

- remove unused imports from ping, shell, and urls command files to clean up code

## v2.6.1 (2025-07-03)

### Feat

- enhance Nexios CLI commands to support optional configuration loading, improve error handling, and update command help descriptions for clarity
- enhance configuration management docs by adding support for .env files, enabling environment-specific settings, and improving validation for required configuration keys
- implement configuration file support for Nexios CLI, allowing app and server options to be defined in `nexios.config.py`, and enhance command functionality to load configurations seamlessly
- add 'URL Configuration' section to documentation and enhance CLI guide with new commands for listing URLs and checking route existence
- enhance app loading by adding auto-search for nexios.config.py and .nexioscli files in the current directory
- add CLI commands to list registered URLs and ping routes in the Nexios application, with support for loading app instances from module paths or config files

### Refactor

- clean up imports in CLI command files and remove unused type hints from ping, shell, and urls modules
- update imports in shell.py to suppress linting warnings and clean up exports in utils module
- remove unused 'normalize_url_path' from exports in utils module
- simplify CLI structure by removing unused utility and validation functions, consolidating command implementations, and enhancing app loading from main module

## v2.6.0 (2025-06-30)

## v2.5.3 (2025-06-30)

### Feat

- enhance server startup by adding support for granian and uvicorn with temporary entry point creation

### Fix

- refine CORS preflight request test by updating allowed methods and headers to match middleware behavior
- update CORS middleware to handle preflight requests more robustly by refining header management and allowing dynamic header responses

### Refactor

- remove main function and update version constraints for pytest in uv.lock

## v2.5.2 (2025-06-29)

### Feat

- enhance NexiosApp.run method to support Granian server

### Fix

- correct spelling of 'exclude_from_schema' in application and routing modules
- update header encoding in StreamingResponse for compatibility
- remove duplicate import of NexiosApp in day22 index documentation

### Refactor

- update error handling UI and enhance JavaScript functionality

## v2.5.1 (2025-06-26)

### Fix

- correct indentation in release workflow for changelog generation step

## v2.5.0 (2025-06-21)

### Feat

- add request verification and enhance locust tests
- introduce context-aware dependency injection system for request-scoped data access

### Fix

- allow optional status code in response methods and default to instance status code

## v2.4.14 (2025-06-20)

### Fix

- handle directory initialization and path formatting in StaticFiles class for improved file serving, closes #136

## v2.4.13 (2025-06-18)

### Fix

- update endpoint path formatting to simplify parameter representation in application.py
- resolve merge conflict by removing unnecessary conflict markers in client.py
- reorder import statements for improved organization in structs.py

### Refactor

- improve code clarity by renaming variables and enhancing type hinting across multiple files
- remove unused imports across various files to clean up the codebase
- update authentication handling and file upload method in API examples

## v2.4.12 (2025-06-15)

## v2.4.11 (2025-06-15)

## v2.4.10 (2025-06-14)

### Fix

- update GitHub Actions workflow to run Tox with uv
- address minor bugs in middleware handling and improve error logging for better debugging

### Refactor

- remove .editorconfig and package-lock.json, update pyproject.toml for Hatchling, enhance requirements.txt, and modify GitHub Actions workflow for uv; adjust middleware usage in application and tests
- consolidate middleware imports and update related references across documentation and codebase

## v2.4.9 (2025-06-06)

### Feat

- **openapi**: enhance API documentation routes with customizable URLs for Swagger and ReDoc; add ReDoc UI generation

### Refactor

- **MakeConfig**: update constructor to accept optional config and kwargs, merging them with defaults for improved flexibility

## v2.4.8 (2025-06-05)

### Feat

- **templating**: add templating guide link in documentation; refactor TemplateEngine for improved configuration handling and error management; update TemplateContextMiddleware for better type hints; remove unused utility functions
- **request**: add properties and methods for enhanced request handling

### Fix

- restore **repr** method in MakeConfig; add warning for missing secret_key in session handling
- **docs**: improve clarity in concurrency guide and update examples for better understanding

### Refactor

- **docs**: update API documentation for clarity and consistency; remove emojis from headings feat(docs): add support for external ASGI apps in routing guide fix(docs): correct async function calls in request handling examples chore: remove outdated ASGI and async Python documentation
- **tests**: remove deprecated error handling test for concurrency utilities

## v2.4.7 (2025-06-01)

### Feat

- **docs**: add 'Concurrency Utilities' section to the guide and update dependency metadata
- **routes**: add test for adding route with path parameters
- **routes**: enhance add_route method to support optional path and handler parameters
- **icon**: redesign SVG icon with gradients, shadows, and new shapes

### Fix

- correct import paths from 'cuncurrency' to 'concurrency' and remove deprecated concurrency utility file
- **docs**: update markdown configuration and correct file data handling in concurrency guide
- **docs**: correct image upload handling in concurrency guide
- **request**: cast session to BaseSessionInterface for type safety
- **application**: restore \_setup_openapi call in handle_lifespan method
- **session**: streamline session configuration access and improve file path handling
- **session**: improve session configuration handling with getattr for safer access
- **readme**: update support icon URL to point to the new documentation site

### Refactor

- **dependencies**: enhance dependency injection to support synchronous and asynchronous handlers
- move utility functions to a new location and remove deprecated files
- **middleware**: rename \_\_middleware to \_middleware and update imports

## v2.4.6 (2025-05-30)

### Fix

- **openapi**: implement OpenAPI setup during application shutdown and improve JSON property typing

## v2.4.5 (2025-05-27)

### Fix

- Remove debug print statements and clean up lifespan event handling
- Remove unnecessary method call in lifespan event handling
- Improve error logging in lifespan event handling and clean up whitespace

## v2.4.4 (2025-05-25)

### Feat

- implement form parsing and routing enhancements with new internal modules

### Fix

- Set default path for Group initialization and add test for external ASGI app integration
- Updates route handling to support both Routes and BaseRoute instances
- improve error message for client disconnection in ASGIRequestResponseBridge

### Refactor

- Remove trailing slash from Group path initialization and clean up unused tests
- Improve type hints and path handling in Group class
- reorganize middleware structure and update routing to use new middleware definitions

## v2.4.3 (2025-05-20)

### Feat

- enhance server error template with improved layout and request information section
- add handler hooks documentation and implement before/after request decorators
- add examples for authentication, exception handling, middleware, request inputs, responses, and routing
- add JWT and API key authentication backends

### Fix

- update workflow to ignore pushes to main branch
- update typing SVG font and styling in README
- correct heading formatting in getting started guide

## v2.4.2 (2025-05-15)

### Feat

- add File Router guide to documentation and update config for navigation
- add ASGI and Async Python guides to documentation
- add ASGI and Async Python guides to documentation

### Fix

- improve JWT import error handling and raise informative exceptions
- update project description for clarity on performance features
- clean up code formatting and add deprecation warning for get_application
- **ci**: improve comments and update PyPI publishing step in release workflow

### Refactor

- update VitePress config for improved structure and clarity
- enhance method detection in APIView for dynamic method registration
- replace get_application with NexiosApp and add startup/shutdown hooks

## v2.4.1 (2025-05-14)

### Feat

- **ci**: add GitHub Actions workflow for automated release on tag push
- **router**: add base_app reference to scope for improved access in request handling

### Fix

- **docs**: remove redundant phrasing in framework description for clarity
- **docs**: simplify installation instructions by removing broken examples
- **docs**: correct GitHub link in VitePress config for accuracy
- **docs**: update version badge from 2.4.0rc1 to 2.4.0 for consistency
- **docs**: add template option to CLI usage instructions fix(docs): update CORS example to include proper configuration setup refactor(response): move remove_header method to improve clarity
- **router**: inherit BaseRouter in Router and WSRouter classes for consistency
- **docs**: remove inline comment from routing example for clarity
- **docs**: remove inline comments from routing example for clarity
- add type hints for version and callable parameters in multiple files
- **router**: remove debug print statement from Router class
- **router**: store reference to the Router instance in scope for better access
- update documentation URL to point to the correct Netlify site
- **cli**: update warning message for clarity on Granian integration
- update version number to 2.4.0 and enhance README for consistency

## v2.4.0 (2025-05-11)

### Feat

- set base path for VitePress configuration
- set base path for VitePress configuration
- add .nojekyll file to prevent GitHub Pages from ignoring files
- add .nojekyll file to prevent GitHub Pages from ignoring \_files
- **docs**: update API Reference link and enhance Getting Started section with version badge
- **docs**: update API Reference link and enhance Getting Started section with version badge
- **docs**: add OpenAPI section to navigation and enhance OpenAPI documentation links
- **docs**: update getting started section to use pip for installation and remove VitePress references
- **docs**: enhance file upload documentation and update site configuration with social links
- **docs**: enhance file upload documentation and update site configuration with social links
- **docs**: update CORS documentation and add file upload guide
- **docs**: update CORS documentation and add file upload guide
- **docs**: enhance API documentation with detailed sections on application, request, response, routing, and WebSocket handling
- **docs**: enhance API documentation with detailed sections on application, request, response, routing, and WebSocket handling
- **docs**: update VitePress config with new meta tags and favicon for improved SEO and branding
- **docs**: add comprehensive CLI documentation including installation, usage, commands, and server selection
- **docs**: enhance WebSocket documentation with new sections on Channels, Groups, and Static Files
- **docs**: add Howto and Websockets sections to navigation and create initial markdown files
- **docs**: add Request Info section with detailed examples for handling HTTP requests
- **docs**: add Authentication and Session Management documentation with examples
- **docs**: add Events section to documentation with usage examples
- **docs**: add manual integration section for pagination with example code
- **docs**: add documentation for Class-Based Views with usage examples and middleware support
- **pagination**: enhance response methods to accept custom data handlers for synchronous and asynchronous pagination
- **pagination**: implement synchronous and asynchronous pagination methods with customizable strategies and data handlers
- **docs**: add 'Error Handling' guide with comprehensive coverage and examples for managing exceptions
- **docs**: enhance headers guide with detailed examples and best practices for request and response headers
- **docs**: add 'Headers' guide with detailed examples for request and response headers
- **docs**: enhance 'Cookies' guide with comprehensive examples and security best practices
- **docs**: add 'Middleware' and 'Cookies' guides to documentation
- **docs**: add 'Routers and Sub-Applications' guide and update navigation
- **docs**: add 'Sending Responses' guide and update navigation
- **routing**: enhance request handling by passing path parameters to route handlers
- **docs**: enhance documentation with getting started and routing guides
- **docs**: add comprehensive documentation and configuration for Nexios framework
- **di**: Enhance dependency injection and add string representation for Request class
- Implement advanced event system with support for priority listeners, event phases, and asynchronous execution
- Add comprehensive overview of Nexios framework in about.md
- Update SUMMARY.md to include comprehensive Dependency Injection section
- Enhance documentation and add dependency injection support in Nexios framework
- Add comprehensive documentation for About section, including Authors, Design Patterns, Performance, and Philosophy
- Enhance dependency injection system with new documentation and integration in routing
- Implement dependency injection system with DependencyProvider and related classes
- Add multi-server support with Uvicorn and Granian in Nexios CLI
- Add example applications and routes for Nexios framework
- Add new project templates with enhanced features and configurations
- Enhance SUMMARY.md with additional sections and improved structure
- Implement comprehensive WebSocket testing suite with multiple endpoints and error handling
- Add WebSocket support and enhance form data handling
- **errors**: Enhance server error handling with detailed debugging information and improved HTML template
- **cli**: Implement CLI tools for project scaffolding and development server management; enhance documentation
- **decorators**: add catch_exception decorator for handling specific exceptions fix(routing): ensure async assertions for route handlers and requests chore(pyproject): update dependencies for jinja2 and pyjwt with optional extras
- **routing**: enhance request handling to support JSON responses

### Fix

- update feature list in README for accuracy and clarity
- update version number and enhance README badges
- remove redundant options and examples from CLI documentation
- remove base path from VitePress configuration
- update base path in VitePress configuration
- set base path in VitePress configuration
- remove base path from VitePress configuration
- update install command to prevent frozen lockfile during dependency installation
- correct whitespace in hero name in index.md
- remove base path from VitePress configuration
- update install command in GitHub Actions workflow for consistency
- update step name for clarity in GitHub Pages deployment
- remove .nojekyll creation step from deploy workflow
- update install command in deploy-docs workflow to use pnpm install
- enable pnpm setup and correct build command formatting in deploy-docs workflow
- **docs**: update metadata and lockfile for improved dependency management
- **app**: correct HTTP request handling in NexiosApp class docs(guide): update installation and routing documentation for clarity
- **docs**: correct path parameter access in room handler and chat endpoint
- **config**: Initialize configuration in NexiosApp constructor
- Correct order of sections in SUMMARY.md for better clarity
- **openapi**: set default type for Schema and update model references
- **static**: improve directory handling and validation in StaticFilesHandler fix(structs): add default value support to RouteParam.get method
- **import**: handle ImportError for Jinja2 with a clear installation message
- **routing**: remove unused response_model parameter and handle empty path case
- **sessions**: correct string representation of session cache
- **application**: set default config if none provided and clean up type ignores fix(exception_handler): refine exception handler type annotations refactor(formparsers): remove unnecessary type ignores and improve readability refactor(request): simplify Request class definition refactor(routing): enhance type annotations and clean up type ignores fix(types): correct response type alias for consistency

### Refactor

- update GitHub Actions workflow for VitePress deployment
- streamline deployment workflow for VitePress
- **cli**: streamline project creation and server run commands, enhance validation functions
- **response**: simplify headers property and update header preservation logic
- **docs**: update response header method references to use set_header
- **routing**: change request_response to async and await its execution in Routes class
- **routing**: move Convertor and related classes to converters.py
- **dependencies**: remove unnecessary inheritance from Any in Depend class
- **types**: remove unused ParamSpec import
- **types**: add ParamSpec for improved type hinting in HandlerType
- remove debug print statements and enhance dependency injection in routing
- **dependencies**: remove old dependency injection implementation and add new one fix(exception_handler): change response from text to json for HTTP exceptions fix(exceptions): update detail type in HTTPException to Any fix(models): update Pydantic model configuration to use ConfigDict test: update assertions in exception handler tests to check for JSON responses
- **minor**: Remove unused TypeVar and clean up lifespan handling in NexiosApp
- Update typing imports and lifespan type annotation in **init**.py
- **docs**: Remove redundant examples and streamline event handling section in events.md
- Improve type annotations and remove unnecessary type ignores across multiple files
- update type annotations for middleware functions to improve clarity and consistency
- enhance type annotations for improved clarity and consistency across application, exception handling, and middleware modules
- streamline type annotations and clean up imports across application, dependencies, routing, and types modules
- Add support for additional route parameters in Router class
- Enhance lifespan shutdown handling in NexiosApp
- Simplify lifespan shutdown handling in NexiosApp
- Update Nexios to use Granian server and enhance configuration options
- Remove WebSocket connection handling from Client class
- Remove debug print statement from ASGI application callable
- **websockets**: rename WebSocketEndpoint to WebSocketConsumer and update imports
- **session**: reorganize session handling and update imports

## v2.3.1 (2025-04-14)

### Feat

- **docs**: add comprehensive documentation for Nexios configuration and hooks
- **funding**: add funding configuration for "Buy Me a Coffee"
- **application**: add responses parameter to route handler

### Fix

- **application**: update default config import and streamline code formatting
- **auth**: remove unused import from jwt backend
- **docs**: improve formatting and clarity in managing_config.md
- **docs**: standardize warning formatting and update hook descriptions in misc.md
- **docs**: add missing links for Managing Config and Misc in SUMMARY.md
- **readme**: update badge alignment and formatting in README files
- **funding**: add GitHub funding link for techwithdunamix
- **tox**: add pytest-asyncio and pydantic dependencies; update asyncio_fixture_scope in pytest options
- **readme**: update image attributes for Swagger API documentation
- **readme**: update visitor count alt text and correct image path
- **docs**: update GzipMiddleware usage in example to use wrap_asgi method
- **router**: handle empty context in render function to prevent errors
- **router**: correct path handling in FileRouter for improved route mapping
- **router**: improve method handling in FileRouter for route mapping
- **router**: fixed method handling and schema exclusion in FileRouter

### Refactor

- **openapi**: streamline OpenAPI configuration and documentation setup
- **transport**: rename request_with_retries to handle_request and improve error handling; update WebSocket connection management refactor(client): change raise_exceptions parameter to raise_app_exceptions for consistency delete(websocketsession): remove unused WebSocketSession file
- **middleware**: update middleware integration and improve ASGI compatibility

## v2.3.0rc2 (2025-04-05)

### Feat

- **router**: add exclude_from_schema option to FileRouter and Router classes

## v2.3.0-rc.1 (2025-04-05)

### Feat

- **logging**: update logging documentation for clarity and consistency; remove deprecated file-router documentation
- **routing**: enhance path parameter replacement using regex for improved flexibility
- **file_router**: add restrict_slash method and improve path handling in route mapping
- **file_router**: implement new HTML rendering functionality and restructure file organization
- **application**: add OpenAPI setup during application startup
- **routing**: enhance route documentation and add get_all_routes method
- **session**: add session configuration enhancements and improve expiration handling
- **auth**: implement session-based authentication backend and enhance session handling
- **exception-handling**: enhance JWT decoding and improve exception handling with custom handlers
- **file-router**: enhance routing configuration with exempt paths and add route decorator
- **file-router**: migrate HTML rendering to file router plugin
- **html-plugin**: adds jinja2 template plugin
- **plugins/file_router.py**: adds middleware support for file router
- **file_router**: refactor route handling to use pathlib for module imports and streamline method mapping
- **plugins/file_router.py**: adds file router plugin
- **openapi**: add OpenAPI configuration and event system documentation refactor(routing_utils): clean up comments and formatting refactor(structs): remove unnecessary comments in type definitions refactor(websockets): improve type annotations and formatting in WebSocketEndpoint
- **openapi**: add Swagger UI generation and auto-documentation capabilities
- **openapi**: enhance path parameter handling and request/response preparation in APIDocumentation
- **openapi**: implement OpenAPI configuration and documentation routes
- **openapi**: add initial OpenAPI models and structure
- **websockets**: add encoding attribute and update middleware type in WebSocketEndpoint class docs: add Nexios Event System Integration Guide with examples and best practices
- **websockets**: add as_route class method to convert WebSocketEndpoint into a route
- **auth**: enhance authentication decorator to accept string or list of scopes
- ✨: add make_response method to create responses using custom response classes; enhance method chaining with preserved headers and cookies
- ✨: add content_length property and set_body method in NexiosResponse; enhance set_headers to support overriding headers in CORS middleware
- 🔧: add lifespan support to NexiosApp and implement close_all_connections method in ChannelBox
- ✨: enhance WebSocketEndpoint with logging capabilities and new channel management methods
- ✨: add GitHub Actions workflow for running tests and uploading coverage reports
- enhance JWT handling and add route-specific middleware decorator
- update authentication backends to improve configuration handling and error reporting
- update project initialization and database configuration templates for improved database connection handling
- enhance Nexios CLI with project initialization and database setup commands
- implement authentication backends and middleware for user authentication
- implement JWT authentication backend and utility functions for token handling
- implement API key and session authentication backends for enhanced security
- implement basic authentication backend and middleware for user authentication
- implement authentication middleware and user classes for enhanced user management
- add request lifecycle decorators for enhanced request handling and logging
- initialize authentication module in the Nexio library
- add parameter validation for route handlers and enhance route decorators
- enhance middleware execution and improve session expiration handling
- update logo to SVG format and adjust mkdocs configuration and request file methods

### Fix

- **routing**: remove unnecessary blank line in Router class
- **cors**: standardize header casing and improve CORS middleware logic
- **session**: correct string representation in BaseSessionInterface and clean up test cases
- **session**: update session expiration logic and improve session management
- **test**: correct typo in first_middleware function parameter name
- **websockets**: remove unused import of MiddlewareType in consumers.py
- **workflow**: update permissions and simplify git push in format-code.yml
- **workflow**: update GitHub token usage in format-code.yml for secure pushing
- **workflow**: update GitHub token secret name in deploy-docs.yml
- **websockets**: import WebsocketRoutes inside as_route method to avoid import errors
- 🔧: correct app reference in handle_http_request; add wrap_with_middleware method to support ASGI middleware integration; improve error handling in BaseMiddleware
- 🔧: suppress RuntimeError in BaseMiddleware to handle EndOfStream gracefully; add type ignore for message assertion
- 🔧: remove debug print statement for message in NexiosApp to clean up output
- 🔧: improve exception handling in collapse_excgroups; update BaseResponse initialization to remove setup parameter and enhance cookie management
- 🔧: update datetime import to use timezone.utc; simplify payload sending logic in Channel class
- 🔧: handle empty range end in FileResponse initialization to prevent ValueError
- 🔧: update FileResponse initialization and improve range handling in response.py; modify BaseMiddleware to suppress RuntimeError; clean up test_response.py
- 🔧: update FileResponse initialization to include setup parameter and clean up range handling comments
- 🔧: update .gitignore, improve gzip documentation, refactor middleware handling, and replace print statements with logger in hooks
- 🔧: ensure websocket is closed properly on disconnect in WebSocketEndpoint
- 🔧: add channel_remove_status variable in ChannelBox and simplify loop in WebSocketEndpoint
- 🔧: make expires parameter optional in Channel class constructor
- 🐛 fix: enhance exception handling by raising exceptions when no handler is present; add user setter to Request class
- simplify method type casting in Request class
- update cookie deletion logic to use None and set expiry to 0
- improve request handling and error logging in NexioApp
- update allowed HTTP methods to lowercase and improve method validation in CORS middleware
- remove debug print statements from response and middleware classes
- remove debug print statements and update CORS headers handling
- re issues

### Refactor

- **examples**: remove unused file router and HTML plugin examples
- **file-router**: refactor routing logic and add utility functions for route management
- **models**: simplify parameter type annotations in OpenAPI models
- **structs**: remove redundant comment in Address class
- **openapi**: remove unused constants and enhance OpenAPIConfig with contact and license fields
- **openapi**: streamline APIDocumentation class and enhance parameter handling
- **style**: clean up whitespace and formatting in application.py and routing.py
- **style**: apply code formatting and clean up whitespace across multiple files
- ♻️: replace getLogger with create_logger and update logo size in README
- ♻️: update documentation for Class-Based Views and remove Class-Based Handlers
- ♻️: update APIView to assign request and response attributes
- ♻️: remove unused import from routing module
- ♻️: remove unused imports and clean up HTTPMethod class in types module
- ♻️: remove APIHandler class; introduce APIView for enhanced class-based views with routing support
- ♻️: reorganize utils and async_helpers; move functions to \_utils and update imports
- 🔧: remove unused middlewares and update FileResponse initialization in response.py
- 🔧: rename \_\_handle_lifespan to handle_lifespan and improve message logging in NexiosApp
- remove database session management and related files
- remove direct authentication middleware instantiation and simplify BasicAuthBackend initialization
- remove BaseConfig dependency and implement global configuration management

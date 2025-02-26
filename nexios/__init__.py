from .application import NexiosApp
from .sessions.middleware import SessionMiddleware
from .middlewares.common import CommonMiddleware
from .middlewares.csrf import CSRFMiddleware
from .config.base import MakeConfig
from .config import set_config, DEFAULT_CONFIG  
from .routing import Router  # type:ignore
from nexios.middlewares.errors.server_error_handler import ServerErrorMiddleware
from .middlewares.cors import CORSMiddleware
from typing import Sequence, Optional
from .application import NexiosApp 

from .types import MiddlewareType, ExceptionHandlerType
from typing_extensions import Doc, Annotated  


def get_application(
    config: Annotated[
        MakeConfig,
        Doc(
            """
                    This subclass is derived from the MakeConfig class and is responsible for managing configurations within the Nexios framework. It takes arguments in the form of dictionaries, allowing for structured and flexible configuration handling. By using dictionaries, this subclass makes it easy to pass multiple configuration values at once, reducing complexity and improving maintainability.

                    One of the key advantages of this approach is its ability to dynamically update and modify settings without requiring changes to the core codebase. This is particularly useful in environments where configurations need to be frequently adjusted, such as database settings, API credentials, or feature flags. The subclass can also validate the provided configuration data, ensuring that incorrect or missing values are handled properly.

                    Additionally, this design allows for merging and overriding configurations, making it adaptable for various use cases. Whether used for small projects or large-scale applications, this subclass ensures that configuration management remains efficient and scalable. By extending MakeConfig, it leverages existing functionality while adding new capabilities tailored to Nexios. This makes it an essential component for maintaining structured and well-organized application settings.
                    """
        ),
    ] = DEFAULT_CONFIG,
    middlewares: Annotated[
        Sequence[MiddlewareType],
        Doc(
            "A list of middlewares, where each middleware is either a class inherited from BaseMiddleware or an asynchronous callable function that accepts request, response, and callnext"
        ),
    ] = [],
    server_error_handler: Annotated[
        Optional[ExceptionHandlerType],
        Doc(
            """
                        A function in Nexios responsible for handling server-side exceptions by logging errors, reporting issues, or initiating recovery mechanisms. It prevents crashes by intercepting unexpected failures, ensuring the application remains stable and operational. This function provides a structured approach to error management, allowing developers to define custom handling strategies such as retrying failed requests, sending alerts, or gracefully degrading functionality. By centralizing error processing, it improves maintainability and observability, making debugging and monitoring more efficient. Additionally, it ensures that critical failures do not disrupt the entire system, allowing services to continue running while appropriately managing faults and failures."""
        ),
    ] = None,
) -> NexiosApp:
    """
    Initializes and returns a `Nexios` application instance, serving as the core entry point for building web applications.

    Nexios is a lightweight, asynchronous Python framework designed for speed, flexibility, and ease of use.
    This function sets up the necessary configurations and routing mechanisms, allowing developers
    to define routes, handle requests, and manage responses efficiently.

    ## Example Usage

    ```python
    from nexios import Nexios
    config = MakeConfig({
        "debug" : True
    })
    app = get_application(config = config)
    ```

    Returns:
        Nexios: An instance of the Nexios application, ready to register routes and handle requests.

    See Also:
        - [Nexios Documentation](https://example.com/nexios-docs)
    """

    set_config(config)

    app = NexiosApp(
        middlewares=[
            ServerErrorMiddleware(handler=server_error_handler),
            CommonMiddleware(),
            CORSMiddleware(),
            SessionMiddleware(),
            CSRFMiddleware(),
            *middlewares,
        ],
        config=config,
    )

    return app


__all__ = [
    "MakeConfig",
    "Router"
]
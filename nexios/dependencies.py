from typing import Any, Callable, Dict, Optional, Type, get_type_hints
from inspect import signature, Parameter
from functools import wraps
import inspect


class Depend:
    def __init__(self, dependency: Optional[Callable] = None):
        self.dependency = dependency


def inject_dependencies(handler: Callable) -> Callable:
    """Decorator to inject dependencies into a route handler while preserving parameter names."""

    @wraps(handler)
    async def wrapped(*args, **kwargs):
        sig = signature(handler)
        bound_args = sig.bind_partial(*args, **kwargs)

        # Get the parameters in order
        params = list(sig.parameters.values())

        for param in params[2:]:
            if (
                param.default != Parameter.empty
                and isinstance(param.default, Depend)
                and param.name not in bound_args.arguments
            ):

                depend = param.default
                dependency_func = depend.dependency

                if dependency_func is None:
                    raise ValueError(
                        f"Dependency for parameter '{param.name}' has no provider"
                    )

                # Resolve the dependency
                if inspect.iscoroutinefunction(dependency_func):
                    bound_args.arguments[param.name] = await dependency_func()
                else:
                    bound_args.arguments[param.name] = dependency_func()

        filtered_kwargs = {
            k: v
            for i, (k, v) in enumerate(bound_args.arguments.items())
            if i >= 2  # Skip first two arguments
        }
        return await handler(*args, **filtered_kwargs)

    return wrapped

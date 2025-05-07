from typing import Callable, Dict, List, Optional, Any
from inspect import signature, Parameter
from functools import wraps
import inspect


class Depend:
    def __init__(self, dependency: Optional[Callable[..., Any]] = None):
        self.dependency = dependency

    def __class_getitem__(cls, item: Any):
        return cls


def inject_dependencies(handler: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to inject dependencies into a route handler while preserving parameter names."""

    @wraps(handler)
    async def wrapped(*args: List[Any], **kwargs: Dict[str, Any]) -> Any:
        sig = signature(handler)
        bound_args = sig.bind_partial(*args, **kwargs)

        # Get the parameters in order
        params = list(sig.parameters.values())

        for param in params:
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

                if hasattr(dependency_func, "__wrapped__"):
                    dependency_func = dependency_func.__wrapped__  # type: ignore[attr-defined]

                dep_sig = signature(dependency_func)
                dep_kwargs = {}

                for dep_param in dep_sig.parameters.values():
                    if dep_param.name in bound_args.arguments:
                        dep_kwargs[dep_param.name] = bound_args.arguments[
                            dep_param.name
                        ]
                    elif dep_param.default != Parameter.empty and isinstance(
                        dep_param.default, Depend
                    ):
                        nested_dep = dep_param.default.dependency
                        if inspect.iscoroutinefunction(nested_dep):
                            dep_kwargs[dep_param.name] = await nested_dep()
                        else:
                            dep_kwargs[dep_param.name] = nested_dep()  # type: ignore[attr-defined]

                # Call the dependency
                if inspect.iscoroutinefunction(dependency_func):
                    bound_args.arguments[param.name] = await dependency_func(
                        **dep_kwargs
                    )
                else:
                    bound_args.arguments[param.name] = dependency_func(**dep_kwargs)

        return await handler(**bound_args.arguments)

    return wrapped

import contextvars
from functools import wraps
import inspect
from inspect import Parameter, signature
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

from nexios.utils.async_helpers import is_async_callable
from nexios.utils.concurrency import run_in_threadpool

if TYPE_CHECKING:
    from nexios import NexiosApp, Router
    from nexios.auth.base import BaseUser
    from nexios.http import Request


class Depend:
    def __init__(self, dependency: Optional[Callable[..., Any]] = None):
        self.dependency = dependency

    def __class_getitem__(cls, item: Any):
        return cls


class Context:
    def __init__(
        self,
        request: Optional["Request"] = None,
        user: Optional["BaseUser"] = None,
        base_app: Optional["NexiosApp"] = None,
        app: Optional["Router"] = None,
        **kwargs,
    ):
        self.request = request
        self.user = user
        self.base_app = base_app
        self.app = app
        for k, v in kwargs.items():
            setattr(self, k, v)


current_context: contextvars.ContextVar[Context] = contextvars.ContextVar(
    "current_context"
)

test_var = 1


def inject_dependencies(handler: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to inject dependencies into a route handler while preserving parameter names and passing context if needed."""

    @wraps(handler)
    async def wrapped(*args: List[Any], **kwargs: Dict[str, Any]) -> Any:
        global test_var
        test_var += 1
        sig = signature(handler)
        bound_args = sig.bind_partial(*args, **kwargs)
        params = list(sig.parameters.values())

        # Pass context if handler accepts it and not already provided
        ctx = None
        try:
            ctx = current_context.get()
        except LookupError:
            ctx = None
        for param in params:
            if (
                isinstance(param.default, Context)
                and param.name not in bound_args.arguments
            ):
                bound_args.arguments[param.name] = ctx

        cleanup_callbacks = []
        # Store cleanup in context if possible
        if ctx is not None:
            if not hasattr(ctx, "_dependency_cleanup"):
                ctx._dependency_cleanup = []
            cleanup_callbacks = ctx._dependency_cleanup
        if ctx.base_app:
            app_dependencies = get_app_dependencies(ctx.base_app.router)
            for dep in app_dependencies:
                dependency_func = dep.dependency
                if dependency_func is None:
                    raise ValueError("Dependency  has no provider")
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
                if inspect.isasyncgenfunction(dependency_func):
                    agen = dependency_func(**dep_kwargs)
                    value = await agen.__anext__()
                    cleanup_callbacks.append(lambda agen=agen: agen.aclose())
                elif inspect.isgeneratorfunction(dependency_func):
                    gen = dependency_func(**dep_kwargs)
                    value = next(gen)
                    cleanup_callbacks.append(lambda gen=gen: gen.close())
                elif inspect.iscoroutinefunction(dependency_func):
                    await dependency_func(**dep_kwargs)
                else:
                    dependency_func(**dep_kwargs)

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

                # Pass context to dependencies if they accept it
                if "context" in dep_sig.parameters and "context" not in dep_kwargs:
                    if ctx is None:
                        try:
                            ctx = current_context.get()
                        except LookupError:
                            ctx = None
                    dep_kwargs["context"] = ctx

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

                if inspect.isasyncgenfunction(dependency_func):
                    agen = dependency_func(**dep_kwargs)
                    value = await agen.__anext__()
                    bound_args.arguments[param.name] = value
                    cleanup_callbacks.append(lambda agen=agen: agen.aclose())
                elif inspect.isgeneratorfunction(dependency_func):
                    gen = dependency_func(**dep_kwargs)
                    value = next(gen)
                    bound_args.arguments[param.name] = value
                    cleanup_callbacks.append(lambda gen=gen: gen.close())
                elif inspect.iscoroutinefunction(dependency_func):
                    bound_args.arguments[param.name] = await dependency_func(
                        **dep_kwargs
                    )
                else:
                    bound_args.arguments[param.name] = dependency_func(**dep_kwargs)

        try:
            if is_async_callable(handler):
                return await handler(**bound_args.arguments)

            else:
                return await run_in_threadpool(handler, **bound_args.arguments)
        finally:
            # Run cleanup callbacks (sync or async)
            for cleanup in cleanup_callbacks:
                result = cleanup()
                if inspect.isawaitable(result):
                    await result

    return wrapped


def get_app_dependencies(router: "Router") -> List[Depend]:
    dependencies = []
    if hasattr(router, "sub_routers"):
        for child_router in router.sub_routers.values():
            dependencies.extend(get_app_dependencies(child_router))
    if hasattr(router, "dependencies"):
        dependencies.extend(router.dependencies)
    return dependencies

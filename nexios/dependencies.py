import contextvars
import inspect
from functools import wraps
from inspect import Parameter, signature
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from nexios.utils.async_helpers import is_async_callable
from nexios.utils.concurrency import run_in_threadpool

if TYPE_CHECKING:
    from nexios import NexiosApp, Router
    from nexios.auth.users.base import BaseUser
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
        **kwargs: Dict[str, Any],
    ):
        self.request = request
        self.user = user
        self.base_app = base_app
        self.app = app
        for k, v in kwargs.items():
            setattr(self, k, v)


current_context: contextvars.ContextVar[Context] = contextvars.ContextVar("current_context")


async def resolve_dependency(
    func: Callable[..., Any],
    ctx: Optional[Context] = None,
    cleanup_callbacks: Optional[List[Callable[[], Any]]] = None,
) -> Any:
    if cleanup_callbacks is None:
        cleanup_callbacks = []

    dep_sig = signature(func)
    dep_kwargs = {}

    for param in dep_sig.parameters.values():
        if param.default != Parameter.empty and isinstance(param.default, Depend):
            nested_func = param.default.dependency
            if nested_func is None:
                raise ValueError(f"Dependency for parameter '{param.name}' has no provider")
            dep_kwargs[param.name] = await resolve_dependency(nested_func, ctx, cleanup_callbacks)
        elif param.default != Parameter.empty and isinstance(param.default, Context):
            dep_kwargs[param.name] = ctx

    if inspect.isasyncgenfunction(func):
        agen = func(**dep_kwargs)
        value = await agen.__anext__()
        cleanup_callbacks.append(lambda agen=agen: agen.aclose())
        return value
    elif inspect.isgeneratorfunction(func):
        gen = func(**dep_kwargs)
        value = next(gen)
        cleanup_callbacks.append(lambda gen=gen: gen.close())
        return value
    elif inspect.iscoroutinefunction(func):
        return await func(**dep_kwargs)
    else:
        return func(**dep_kwargs)


def inject_dependencies(handler: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to inject dependencies into a route handler while supporting deep DI."""

    @wraps(handler)
    async def wrapped(*args: List[Any], **kwargs: Dict[str, Any]) -> Any:
        sig = signature(handler)
        bound_args = sig.bind_partial(*args, **kwargs)
        params = list(sig.parameters.values())

        try:
            ctx = current_context.get()
        except LookupError:
            ctx = None

        cleanup_callbacks: List[Callable[[], Any]] = []
        if ctx is not None and not hasattr(ctx, "_dependency_cleanup"):
            setattr(ctx, "_dependency_cleanup", [])
        if ctx is not None:
            cleanup_callbacks = getattr(ctx, "_dependency_cleanup")

        if ctx is not None and ctx.base_app:
            app_dependencies = get_app_dependencies(ctx.base_app.router)
            for dep in app_dependencies:
                dependency_func = dep.dependency
                if dependency_func is None:
                    raise ValueError("Dependency has no provider")
                await resolve_dependency(dependency_func, ctx, cleanup_callbacks)

        for param in params:
            if (
                param.default != Parameter.empty
                and isinstance(param.default, Depend)
                and param.name not in bound_args.arguments
            ):
                depend = param.default
                dependency_func = depend.dependency
                if dependency_func is None:
                    raise ValueError(f"Dependency for parameter '{param.name}' has no provider")

                bound_args.arguments[param.name] = await resolve_dependency(
                    dependency_func, ctx, cleanup_callbacks
                )

        try:
            if is_async_callable(handler):
                return await handler(**bound_args.arguments)
            else:
                return await run_in_threadpool(handler, **bound_args.arguments)
        finally:
            for cleanup in reversed(cleanup_callbacks):
                result = cleanup()
                if inspect.isawaitable(result):
                    await result

    return wrapped



def get_app_dependencies(router: "Router") -> List[Depend]:
    dependencies: List[Depend] = []
    if hasattr(router, "sub_routers"):
        for child_router in router.sub_routers.values():
            dependencies.extend(get_app_dependencies(child_router))  # type: ignore[arg-type]
    if hasattr(router, "dependencies"):
        dependencies.extend(router.dependencies)
    return dependencies

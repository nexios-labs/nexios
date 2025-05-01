import asyncio
import inspect
from enum import Enum
from functools import wraps
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set, Type, TypeVar, Union, get_type_hints

from nexios.http import Request, Response

T = TypeVar("T")


class DependencyError(Exception):
    """Base exception for dependency injection errors."""
    pass


class CircularDependencyError(DependencyError):
    """Raised when a circular dependency is detected."""
    pass


class DependencyResolutionError(DependencyError):
    """Raised when a dependency cannot be resolved."""
    pass


class DependencyScope(Enum):
    """Scope for dependencies."""
    REQUEST = "request"
    # Can be extended with other scopes in the future
    # Example: APPLICATION, SESSION, etc.


class Depends:
    """
    Marks a function parameter as a dependency.
    
    Dependencies are resolved recursively, and the results are cached for the
    duration of the request.
    
    Example:
        async def get_db():
            return db_connection
            
        async def get_user(db = Depends(get_db)):
            return await db.get_user()
            
        @app.get("/users/{id}")
        async def get_user_route(request, response, user = Depends(get_user)):
            return {"user": user}
    """
    
    def __init__(
        self, 
        dependency: Callable[..., Any],
        use_cache: bool = True,
        scope: DependencyScope = DependencyScope.REQUEST
    ):
        """
        Initialize a dependency.
        
        Args:
            dependency: The dependency function to execute.
            use_cache: Whether to cache the result of this dependency.
            scope: The scope of the dependency.
        """
        self.dependency = dependency
        self.use_cache = use_cache
        self.scope = scope
        
    def __repr__(self) -> str:
        return f"Depends({self.dependency.__name__})"


class DependencyCache:
    """
    Cache for storing resolved dependencies during a request.
    """
    
    def __init__(self):
        self.cache: Dict[Callable[..., Any], Any] = {}
        
    def get(self, dependency: Callable[..., Any]) -> Any:
        """Get a cached dependency value."""
        return self.cache.get(dependency)
        
    def set(self, dependency: Callable[..., Any], value: Any) -> None:
        """Set a cached dependency value."""
        self.cache[dependency] = value
        
    def has(self, dependency: Callable[..., Any]) -> bool:
        """Check if a dependency is in the cache."""
        return dependency in self.cache
        
    def clear(self) -> None:
        """Clear the cache."""
        self.cache.clear()


class DependencyResolver:
    """
    Resolves dependencies recursively.
    """
    
    def __init__(self):
        self.cache = DependencyCache()
        
  
    async def resolve_dependencies(
        self, 
        func: Callable[..., Any], 
        request: Request,
        response: Response,
        param_values: Dict[str, Any] = None,
        seen: Optional[Set[Callable[..., Any]]] = None
    ) -> Dict[str, Any]:
        if seen is None:
            seen = set()
            
        if func in seen:
            raise CircularDependencyError(f"Circular dependency detected: {func.__name__}")
            
        seen.add(func)
        
        signature = inspect.signature(func)
        params = signature.parameters
        values: Dict[str, Any] = {}
        param_values = param_values or {}

        # Get parameter names in order
        param_names = list(params.keys())
        
        # Try to inject request and response based on parameter names and types
        for i, name in enumerate(param_names):
            param = params[name]
            annotation = param.annotation
            
            # First parameter - try to inject request
            if i == 0 and name not in param_values:
                if (annotation is inspect.Parameter.empty or 
                    isinstance(request, annotation)):
                    param_values[name] = request
            
            # Second parameter - try to inject response
            elif i == 1 and name not in param_values:
                if (annotation is inspect.Parameter.empty or 
                    isinstance(response, annotation)):
                    param_values[name] = response

        # Rest of the existing resolution logic...
        for name, param in params.items():
            if name in param_values:
                values[name] = param_values[name]
                continue
                
            if (param.default != inspect.Parameter.empty and 
                isinstance(param.default, Depends)):
                depends = param.default
                dependency_func = depends.dependency
                
                if depends.use_cache and self.cache.has(dependency_func):
                    values[name] = self.cache.get(dependency_func)
                    continue
                
                sub_dependencies = await self.resolve_dependencies(
                    dependency_func, request, response, param_values, seen.copy()
                )
                result = dependency_func(**sub_dependencies)
                
                if asyncio.iscoroutine(result):
                    result = await result
                    
                if depends.use_cache:
                    self.cache.set(dependency_func, result)
                    
                values[name] = result
            elif param.default != inspect.Parameter.empty:
                values[name] = param.default
                
        seen.remove(func)
        return values
class DependencyProvider:
    """
    Provides dependencies for route handlers.
    """
    
    def __init__(self):
        """Initialize the dependency provider."""
        self.resolver = DependencyResolver()
        
    async def get_dependencies(
        self, 
        func: Callable[..., Any], 
        request: Request,
        response: Response,
        param_values: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Get all dependencies for a function.
        
        Args:
            func: The function whose dependencies to get.
            request: The HTTP request.
            response: The HTTP response.
            param_values: Additional parameter values to use.
            
        Returns:
            A dictionary of parameter names to resolved dependency values.
        """
        try:
            return await self.resolver.resolve_dependencies(
                func, 
                request, 
                response,
                param_values
            )
        except Exception as e:
            if isinstance(e, DependencyError):
                raise
            raise DependencyResolutionError(
                f"Failed to resolve dependencies for {func.__name__}: {str(e)}"
            ) from e
            
    def clear_cache(self) -> None:
        """Clear the dependency cache."""
        self.resolver.clear_cache()



dependency_provider = DependencyProvider()
handler = lambda req, res: None  # Dummy handler for demonstration purposes 


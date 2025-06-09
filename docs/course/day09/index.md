# 🚀 Day 9: JWT Auth (Part 2)

## Token Rotation

Implementing token rotation for enhanced security:

```python
from nexios import get_application
from nexios.security import JWTAuthBackend, create_access_token
from datetime import datetime, timedelta
import jwt

app = get_application()

# Configure JWT with refresh token support
auth = JWTAuthBackend(
    secret_key="your-secret-key",
    algorithm="HS256",
    access_token_expiration=timedelta(minutes=15),
    refresh_token_expiration=timedelta(days=7)
)

app.auth_backend = auth

@app.post("/auth/login")
async def login(request: Request):
    data = await request.json()
    user = await validate_user(data["username"], data["password"])
    
    if not user:
        return Response(
            content={"error": "Invalid credentials"},
            status_code=401
        )
    
    # Create both access and refresh tokens
    access_token = await create_access_token(
        data={"sub": str(user.id)},
        expires_delta=auth.access_token_expiration
    )
    
    refresh_token = await create_access_token(
        data={
            "sub": str(user.id),
            "type": "refresh"
        },
        expires_delta=auth.refresh_token_expiration
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.post("/auth/refresh")
async def refresh_token(request: Request):
    data = await request.json()
    refresh_token = data.get("refresh_token")
    
    if not refresh_token:
        return Response(
            content={"error": "Refresh token required"},
            status_code=400
        )
    
    try:
        # Verify refresh token
        payload = await auth.verify_token(refresh_token)
        
        # Check if it's a refresh token
        if payload.get("type") != "refresh":
            raise jwt.InvalidTokenError("Invalid token type")
        
        # Create new access token
        access_token = await create_access_token(
            data={"sub": payload["sub"]},
            expires_delta=auth.access_token_expiration
        )
        
        return {"access_token": access_token}
        
    except jwt.InvalidTokenError:
        return Response(
            content={"error": "Invalid refresh token"},
            status_code=401
        )
```

## Token Expiration

Managing token expiration and validation:

```python
from nexios.security import TokenValidator
from datetime import datetime, timezone

class TokenExpirationHandler:
    def __init__(self, max_token_age: timedelta):
        self.max_token_age = max_token_age
    
    async def validate_token(self, token: str) -> bool:
        try:
            payload = await auth.verify_token(token)
            
            # Check expiration
            exp = datetime.fromtimestamp(
                payload["exp"],
                tz=timezone.utc
            )
            
            if datetime.now(timezone.utc) >= exp:
                return False
            
            # Check token age
            iat = datetime.fromtimestamp(
                payload["iat"],
                tz=timezone.utc
            )
            
            age = datetime.now(timezone.utc) - iat
            if age > self.max_token_age:
                return False
            
            return True
            
        except jwt.InvalidTokenError:
            return False

# Use in middleware
expiration_handler = TokenExpirationHandler(
    max_token_age=timedelta(days=1)
)

@app.middleware("http")
async def validate_token_age(request: Request, call_next):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        
        if not await expiration_handler.validate_token(token):
            return Response(
                content={"error": "Token expired"},
                status_code=401
            )
    
    return await call_next(request)
```

## Custom Claims

Adding custom claims to tokens:

```python
from typing import Dict, Any

class CustomClaimsHandler:
    @staticmethod
    async def add_custom_claims(user: User) -> Dict[str, Any]:
        return {
            "username": user.username,
            "email": user.email,
            "roles": user.roles,
            "permissions": await get_user_permissions(user),
            "org_id": str(user.organization_id),
            "is_premium": user.is_premium,
            "last_login": datetime.now(timezone.utc).isoformat()
        }

@app.post("/auth/login")
async def login_with_claims(request: Request):
    data = await request.json()
    user = await validate_user(data["username"], data["password"])
    
    if not user:
        return Response(
            content={"error": "Invalid credentials"},
            status_code=401
        )
    
    # Add custom claims
    claims = await CustomClaimsHandler.add_custom_claims(user)
    claims["sub"] = str(user.id)
    
    # Create token with claims
    token = await create_access_token(data=claims)
    
    return {"access_token": token, "token_type": "bearer"}
```

## JTI Blacklisting

Implementing token blacklisting:

```python
from nexios.cache import RedisCache
import uuid

class TokenBlacklist:
    def __init__(self):
        self.cache = RedisCache()
    
    async def add_to_blacklist(
        self,
        token: str,
        reason: str = "logout",
        expires_in: int = 86400  # 24 hours
    ):
        jti = str(uuid.uuid4())
        await self.cache.set(
            f"blacklist:{jti}",
            {
                "token": token,
                "reason": reason,
                "blacklisted_at": datetime.now(timezone.utc).isoformat()
            },
            expire=expires_in
        )
        return jti
    
    async def is_blacklisted(self, jti: str) -> bool:
        return await self.cache.exists(f"blacklist:{jti}")
    
    async def get_blacklist_info(self, jti: str) -> dict:
        return await self.cache.get(f"blacklist:{jti}")

# Initialize blacklist
blacklist = TokenBlacklist()

@app.post("/auth/logout")
async def logout(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return Response(
            content={"error": "No token provided"},
            status_code=400
        )
    
    token = auth_header.split(" ")[1]
    jti = await blacklist.add_to_blacklist(token, reason="logout")
    
    return {
        "message": "Successfully logged out",
        "jti": jti
    }

# Middleware to check blacklist
@app.middleware("http")
async def check_blacklist(request: Request, call_next):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        payload = await auth.verify_token(token)
        
        if "jti" in payload:
            if await blacklist.is_blacklisted(payload["jti"]):
                return Response(
                    content={"error": "Token has been revoked"},
                    status_code=401
                )
    
    return await call_next(request)
```

## 📝 Practice Exercise

1. Implement token rotation system:
   - Access token refresh
   - Sliding session expiration
   - Token revocation

2. Add custom claims:
   - User permissions
   - Organization data
   - Device information

3. Create token management system:
   - Token blacklisting
   - Active sessions tracking
   - Token usage analytics

## 📚 Additional Resources
- [JWT Claims](https://auth0.com/docs/tokens/json-web-tokens/json-web-token-claims)
- [Token Security](https://nexios.dev/guide/token-security)
- [Redis Integration](https://nexios.dev/guide/redis)
- [Session Management](https://nexios.dev/guide/sessions)

## 🎯 Next Steps
Tomorrow in [Day 10: API Key Authentication](../day10/index.md), we'll explore:
- Creating API keys
- Validating API keys
- Using keys in headers or query params
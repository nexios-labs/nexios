# Day 16: Testing Microservices

Welcome to Day 16! Today we'll learn how to effectively test microservices.

## Testing Strategy

Key aspects:
- Unit Testing
- Integration Testing
- Contract Testing
- End-to-End Testing
- Performance Testing
- Chaos Testing
- Security Testing
- Monitoring

## Test Framework

```python
import pytest
import asyncio
import aiohttp
import docker
import asyncpg
import aioredis
from typing import Dict, Any, AsyncGenerator
import json
import os
from dataclasses import dataclass

@dataclass
class TestConfig:
    database_url: str
    redis_url: str
    registry_url: str
    service_url: str

@pytest.fixture
async def config() -> TestConfig:
    """Test configuration"""
    return TestConfig(
        database_url="postgresql://test:test@localhost:5432/test",
        redis_url="redis://localhost:6379/1",
        registry_url="http://localhost:8001",
        service_url="http://localhost:8000"
    )

@pytest.fixture
async def docker_client():
    """Docker client for container management"""
    return docker.from_env()

@pytest.fixture
async def database(config: TestConfig):
    """Database connection"""
    conn = await asyncpg.connect(config.database_url)
    
    # Setup test database
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    """)
    
    yield conn
    
    # Cleanup
    await conn.execute("DROP TABLE users")
    await conn.close()

@pytest.fixture
async def redis(config: TestConfig):
    """Redis connection"""
    client = aioredis.from_url(config.redis_url)
    
    yield client
    
    # Cleanup
    await client.flushdb()
    await client.close()

@pytest.fixture
async def http_client():
    """HTTP client for API testing"""
    async with aiohttp.ClientSession() as session:
        yield session

class TestService:
    """Base class for service tests"""
    
    def __init__(
        self,
        config: TestConfig,
        database,
        redis,
        http_client
    ):
        self.config = config
        self.db = database
        self.redis = redis
        self.http = http_client
    
    async def create_user(self, data: Dict[str, Any]):
        """Create test user"""
        async with self.http.post(
            f"{self.config.service_url}/users",
            json=data
        ) as response:
            return await response.json()
    
    async def get_user(self, user_id: int):
        """Get test user"""
        async with self.http.get(
            f"{self.config.service_url}/users/{user_id}"
        ) as response:
            return await response.json()

@pytest.fixture
async def service(
    config: TestConfig,
    database,
    redis,
    http_client
):
    """Service test helper"""
    return TestService(
        config,
        database,
        redis,
        http_client
    )

# Unit Tests
async def test_create_user(service: TestService):
    """Test user creation"""
    # Create user
    user_data = {
        "name": "Test User",
        "email": "test@example.com"
    }
    
    response = await service.create_user(user_data)
    
    assert response["name"] == user_data["name"]
    assert response["email"] == user_data["email"]
    assert "id" in response
    
    # Verify in database
    user = await service.db.fetchrow(
        "SELECT * FROM users WHERE id = $1",
        response["id"]
    )
    
    assert user["name"] == user_data["name"]
    assert user["email"] == user_data["email"]

async def test_get_user(service: TestService):
    """Test user retrieval"""
    # Create test user
    user_data = {
        "name": "Test User",
        "email": "test@example.com"
    }
    
    created = await service.create_user(user_data)
    
    # Get user
    user = await service.get_user(created["id"])
    
    assert user["id"] == created["id"]
    assert user["name"] == user_data["name"]
    assert user["email"] == user_data["email"]

async def test_user_not_found(service: TestService):
    """Test user not found"""
    async with service.http.get(
        f"{service.config.service_url}/users/999"
    ) as response:
        assert response.status == 404
        data = await response.json()
        assert "error" in data

# Integration Tests
class TestUserService:
    @pytest.fixture
    async def auth_token(self, service: TestService):
        """Get authentication token"""
        async with service.http.post(
            f"{service.config.service_url}/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        ) as response:
            data = await response.json()
            return data["token"]
    
    async def test_create_order(
        self,
        service: TestService,
        auth_token: str
    ):
        """Test order creation with authentication"""
        # Create order
        order_data = {
            "items": [
                {"product_id": 1, "quantity": 2},
                {"product_id": 2, "quantity": 1}
            ]
        }
        
        async with service.http.post(
            f"{service.config.service_url}/orders",
            json=order_data,
            headers={"Authorization": auth_token}
        ) as response:
            assert response.status == 201
            order = await response.json()
            
            assert "id" in order
            assert order["items"] == order_data["items"]
            assert "user_id" in order
    
    async def test_unauthorized_access(
        self,
        service: TestService
    ):
        """Test unauthorized access"""
        async with service.http.get(
            f"{service.config.service_url}/orders"
        ) as response:
            assert response.status == 401

# Contract Tests
from pact import Consumer, Provider

@pytest.fixture
def pact():
    """Pact contract testing"""
    return Consumer("OrderService").has_pact_with(
        Provider("UserService"),
        pact_dir="./pacts"
    )

async def test_user_service_contract(pact):
    """Test user service contract"""
    expected = {
        "id": 1,
        "name": "Test User",
        "email": "test@example.com"
    }
    
    (pact
        .given("User exists")
        .upon_receiving("a request for user")
        .with_request(
            method="GET",
            path="/users/1"
        )
        .will_respond_with(
            status=200,
            body=expected
        ))
    
    with pact:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{pact.uri}/users/1"
            ) as response:
                user = await response.json()
                assert user == expected

# Performance Tests
from locust import HttpUser, task, between

class UserServiceTest(HttpUser):
    wait_time = between(1, 2)
    
    @task
    def get_user(self):
        """Test user retrieval performance"""
        self.client.get(
            f"/users/{random.randint(1, 100)}",
            headers={"Authorization": self.token}
        )
    
    @task
    def create_user(self):
        """Test user creation performance"""
        self.client.post(
            "/users",
            json={
                "name": f"User {random.randint(1, 1000)}",
                "email": f"user{random.randint(1, 1000)}@example.com"
            },
            headers={"Authorization": self.token}
        )
    
    def on_start(self):
        """Get authentication token"""
        response = self.client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        self.token = response.json()["token"]

# Chaos Testing
async def test_database_failure(
    service: TestService,
    docker_client
):
    """Test service behavior with database failure"""
    # Stop database container
    container = docker_client.containers.get("postgres")
    container.stop()
    
    # Test service response
    async with service.http.get(
        f"{service.config.service_url}/users/1"
    ) as response:
        assert response.status == 503
        data = await response.json()
        assert "error" in data
    
    # Restart database
    container.start()

async def test_redis_failure(
    service: TestService,
    docker_client
):
    """Test service behavior with cache failure"""
    # Stop Redis container
    container = docker_client.containers.get("redis")
    container.stop()
    
    # Test service response
    async with service.http.get(
        f"{service.config.service_url}/users/1"
    ) as response:
        assert response.status == 200
        data = await response.json()
        assert "id" in data
    
    # Restart Redis
    container.start()

# Security Tests
async def test_sql_injection(service: TestService):
    """Test SQL injection prevention"""
    async with service.http.get(
        f"{service.config.service_url}/users/1' OR '1'='1"
    ) as response:
        assert response.status == 400
        data = await response.json()
        assert "error" in data

async def test_xss_prevention(service: TestService):
    """Test XSS prevention"""
    user_data = {
        "name": "<script>alert('xss')</script>",
        "email": "test@example.com"
    }
    
    response = await service.create_user(user_data)
    assert "<script>" not in response["name"]

# End-to-End Tests
class TestEcommerce:
    async def test_purchase_flow(
        self,
        service: TestService,
        auth_token: str
    ):
        """Test complete purchase flow"""
        # 1. Add to cart
        cart_data = {
            "product_id": 1,
            "quantity": 2
        }
        
        async with service.http.post(
            f"{service.config.service_url}/cart/items",
            json=cart_data,
            headers={"Authorization": auth_token}
        ) as response:
            assert response.status == 201
            cart = await response.json()
        
        # 2. Create order
        async with service.http.post(
            f"{service.config.service_url}/orders",
            json={"cart_id": cart["id"]},
            headers={"Authorization": auth_token}
        ) as response:
            assert response.status == 201
            order = await response.json()
        
        # 3. Process payment
        payment_data = {
            "order_id": order["id"],
            "token": "tok_visa"
        }
        
        async with service.http.post(
            f"{service.config.service_url}/payments",
            json=payment_data,
            headers={"Authorization": auth_token}
        ) as response:
            assert response.status == 201
            payment = await response.json()
            assert payment["status"] == "succeeded"
        
        # 4. Verify order status
        async with service.http.get(
            f"{service.config.service_url}/orders/{order['id']}",
            headers={"Authorization": auth_token}
        ) as response:
            assert response.status == 200
            updated_order = await response.json()
            assert updated_order["status"] == "paid"
        
        # 5. Check inventory
        async with service.http.get(
            f"{service.config.service_url}/products/1"
        ) as response:
            assert response.status == 200
            product = await response.json()
            assert product["stock"] == 8  # Initial 10 - 2

# Test Configuration
pytest_plugins = [
    "pytest_asyncio",
    "pytest_docker_compose"
]

def pytest_configure(config):
    """Configure test environment"""
    os.environ["TESTING"] = "1"
    os.environ["DATABASE_URL"] = (
        "postgresql://test:test@localhost:5432/test"
    )
    os.environ["REDIS_URL"] = "redis://localhost:6379/1"

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    """Docker compose file for testing"""
    return os.path.join(
        str(pytestconfig.rootdir),
        "docker-compose.test.yml"
    )

@pytest.fixture(scope="session")
def docker_compose_project_name():
    """Docker compose project name"""
    return "test_microservices"
```

## Docker Compose for Testing

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: test
    ports:
      - "5432:5432"
  
  redis:
    image: redis:6
    ports:
      - "6379:6379"
  
  registry:
    build:
      context: .
      dockerfile: registry/Dockerfile
    environment:
      - REDIS_URL=redis://redis:6379
    ports:
      - "8001:8001"
    depends_on:
      - redis
  
  user-service:
    build:
      context: .
      dockerfile: services/user/Dockerfile
    environment:
      - DATABASE_URL=postgresql://test:test@postgres:5432/test
      - REDIS_URL=redis://redis:6379
      - REGISTRY_URL=http://registry:8001
    ports:
      - "8002:8000"
    depends_on:
      - postgres
      - redis
      - registry
  
  order-service:
    build:
      context: .
      dockerfile: services/order/Dockerfile
    environment:
      - DATABASE_URL=postgresql://test:test@postgres:5432/test
      - REDIS_URL=redis://redis:6379
      - REGISTRY_URL=http://registry:8001
    ports:
      - "8003:8000"
    depends_on:
      - postgres
      - redis
      - registry
  
  product-service:
    build:
      context: .
      dockerfile: services/product/Dockerfile
    environment:
      - DATABASE_URL=postgresql://test:test@postgres:5432/test
      - REDIS_URL=redis://redis:6379
      - REGISTRY_URL=http://registry:8001
    ports:
      - "8004:8000"
    depends_on:
      - postgres
      - redis
      - registry
```

## Test Runner Script

```python
# run_tests.py
import asyncio
import pytest
import os
import docker
import time
import logging
from typing import List

async def wait_for_services():
    """Wait for all services to be ready"""
    async with aiohttp.ClientSession() as session:
        services = [
            "http://localhost:8001",  # Registry
            "http://localhost:8002",  # User Service
            "http://localhost:8003",  # Order Service
            "http://localhost:8004"   # Product Service
        ]
        
        while True:
            try:
                # Check all services
                results = await asyncio.gather(*[
                    session.get(f"{service}/health")
                    for service in services
                ], return_exceptions=True)
                
                # Check if all are healthy
                if all(
                    not isinstance(r, Exception) and
                    r.status == 200
                    for r in results
                ):
                    break
            except:
                pass
            
            await asyncio.sleep(1)

async def run_tests():
    """Run test suite"""
    # Start containers
    client = docker.from_env()
    
    try:
        # Build and start services
        os.system(
            "docker-compose -f docker-compose.test.yml up -d"
        )
        
        # Wait for services
        await wait_for_services()
        
        # Run tests
        result = pytest.main([
            "tests",
            "-v",
            "--cov=services",
            "--cov-report=html",
            "--cov-report=term"
        ])
        
        return result
        
    finally:
        # Cleanup
        os.system(
            "docker-compose -f docker-compose.test.yml down"
        )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Run tests
    result = asyncio.run(run_tests())
    
    # Exit with test result
    exit(result)
```

## Key Concepts Learned

- Test Strategy
- Unit Testing
- Integration Testing
- Contract Testing
- Performance Testing
- Chaos Testing
- Security Testing
- End-to-End Testing
- Test Infrastructure
- Continuous Testing

## Additional Resources

- [Testing Microservices](https://martinfowler.com/articles/microservice-testing/)
- [Pact Contract Testing](https://docs.pact.io/)
- [Locust Load Testing](https://locust.io/)
- [Chaos Engineering](https://principlesofchaos.org/)
- [Security Testing](https://owasp.org/www-project-web-security-testing-guide/)

## Homework

1. Create Test Suite:
   - Unit tests
   - Integration tests
   - Contract tests
   - Performance tests
   - Security tests

2. Setup CI/CD Pipeline:
   - Automated testing
   - Test environments
   - Test reporting
   - Coverage analysis

3. Implement Chaos Tests:
   - Network failures
   - Service failures
   - Database failures
   - Load testing

## Next Steps

Tomorrow, we'll explore [Day 17: Monitoring and Observability](../day17/index.md). 


# Response API Reference


## Handler Signature 
```python 
async def handler(req: Request, response: Response) -> Response:
    # Usage examples below
```

##  Core Methods 

### 1. Setting Response Type

#### `text()`
```python
.text(content: str, status_code: int = 200, headers: Dict[str, Any] = {}) -> Response
```
- Sets plain text response
- Example:
  ```python
  return response.text("Hello World")
  ```

#### `json()`
```python
.json(
    data: Union[str, List[Any], Dict[str, Any]],
    status_code: int = 200,
    headers: Dict[str, Any] = {},
    indent: Optional[int] = None,
    ensure_ascii: bool = True
) -> Response
```
- Sets JSON response
- Example:
  ```python
  return response.json({"key": "value"}, indent=2)
  ```

#### `html()`
```python
.html(content: str, status_code: int = 200, headers: Dict[str, Any] = {}) -> Response
```
- Sets HTML response
- Example:
  ```python
  return response.html("<h1>Hello</h1>")
  ```

#### `file()`
```python
.file(
    path: Union[str, Path],
    filename: Optional[str] = None,
    content_disposition_type: str = "inline"
) -> Response
```
- Sends file response
- Example:
  ```python
  return response.file("/path/to/file.pdf")
  ```

#### `download()`
```python
.download(path: Union[str, Path], filename: Optional[str] = None) -> Response
```
- Forces file download
- Example:
  ```python
  return response.download("/path/to/file.zip")
  ```

#### `stream()`
```python
.stream(
    iterator: Generator[Union[str, bytes], Any, Any],
    content_type: str = "text/plain",
    status_code: Optional[int] = None
) -> Response
```
- Streams response
- Example:
  ```python
  def gen():
      yield "streaming"
      yield "content"
  return response.stream(gen())
  ```

#### `redirect()`
```python
.redirect(url: str, status_code: int = 302) -> Response
```
- Redirects to URL
- Example:
  ```python
  return response.redirect("/new-location")
  ```

#### `empty()`
```python
.empty(status_code: int = 200, headers: Dict[str, Any] = {}) -> Response
```
- Empty response body
- Example:
  ```python
  return response.empty(status_code=204)
  ```

### 2. Headers & Cookies

#### `set_header()`
```python
.set_header(key: str, value: str, overide: bool = False) -> Response
```
- Sets response header
- Example:
  ```python
  return response.set_header("X-Custom", "value")
  ```

#### `set_headers()`
```python
.set_headers(headers: Dict[str, str], overide_all: bool = False) -> Response
```
- Sets multiple headers
- Example:
  ```python
  return response.set_headers({"X-One": "1", "X-Two": "2"})
  ```

#### `remove_header()`
```python
.remove_header(key: str) -> Response
```
- Removes header
- Example:
  ```python
  return response.remove_header("X-Remove-Me")
  ```

#### `set_cookie()`
```python
.set_cookie(
    key: str,
    value: str,
    max_age: Optional[int] = None,
    expires: Optional[Union[str, datetime, int]] = None,
    path: str = "/",
    domain: Optional[str] = None,
    secure: bool = True,
    httponly: bool = False,
    samesite: Optional[Literal["lax", "strict", "none"]] = "lax"
) -> Response
```
- Sets cookie
- Example:
  ```python
  return response.set_cookie("session", "abc123", httponly=True)
  ```

#### `set_permanent_cookie()`
```python
.set_permanent_cookie(key: str, value: str, **kwargs: Dict[str, Any]) -> Response
```
- Sets cookie with 10-year expiration
- Example:
  ```python
  return response.set_permanent_cookie("user_id", "1234")
  ```

#### `delete_cookie()`
```python
.delete_cookie(
    key: str,
    path: str = "/",
    domain: Optional[str] = None
) -> Response
```
- Deletes cookie
- Example:
  ```python
  return response.delete_cookie("old_cookie")
  ```

### 3. Response Configuration

#### `status()`
```python
.status(status_code: int) -> Response
```
- Sets HTTP status code
- Example:
  ```python
  return response.status(404)
  ```

#### `cache()`
```python
.cache(max_age: int = 3600, private: bool = True) -> Response
```
- Enables caching
- Example:
  ```python
  return response.cache(max_age=86400)
  ```

#### `no_cache()`
```python
.no_cache() -> Response
```
- Disables caching
- Example:
  ```python
  return response.no_cache()
  ```

## Properties

```python
.headers: MutableHeaders  # All current headers
.cookies: List[Dict[str, Any]]  # All cookies
.body: Union[bytes, memoryview]  # Response body
.content_type: Optional[str]  # Content-Type header
.content_length: str  # Content-Length
```

## Advanced Usage

### `make_response()`
```python
.make_response(response_class: BaseResponse) -> Response
```
- Uses custom response class while preserving headers/cookies
- Example:
  ```python
  custom_resp = CustomResponse()
  return response.make_response(custom_resp)
  ```

### `resp()`
```python
.resp(
    body: Union[JSONType, Any] = "",
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None,
    content_type: str = "text/plain"
) -> Response
```
- Low-level response configuration
- Example:
  ```python
  return response.resp(b"raw", content_type="application/octet-stream")
  ```

---


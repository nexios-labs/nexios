from nexios.middlewares.base import BaseMiddleware
from nexios.http import Request, Response
from nexios.config import get_config
import traceback, html, sys, inspect, typing, platform, json, datetime, uuid, os
from nexios.logging import DEBUG, create_logger
from nexios.__main__ import __version__ as nexios_version

logger = create_logger(__name__, log_level=DEBUG)
STYLES = """

:root {
    --primary: #10b981;
    --primary-dark: #059669;
    --primary-light: #d1fae5;
    --secondary: #14b8a6;
    --background: #0f172a;
    --surface: #1e293b;
    --surface-light: #334155;
    --error: #ef4444;
    --text: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-tertiary: #64748b;
    --border: #334155;
    --code-bg: #1e293b;
    --code-fg: #a5f3fc;
    --highlight: #eab308;
    --highlight-bg: rgba(234, 179, 8, 0.1);
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background-color: var(--background);
    color: var(--text);
    margin: 0;
    padding: 0;
    line-height: 1.6;
    font-size: 15px;
}

h1, h2, h3, h4, h5, h6 {
    font-weight: 600;
    line-height: 1.4;
}

h1 {
    color: var(--primary);
    font-size: 24px;
    margin-bottom: 4px;
}

h2 {
    color: var(--text);
    font-size: 18px;
    margin-top: 4px;
    margin-bottom: 16px;
    font-weight: 500;
}

h3 {
    color: var(--primary);
    font-size: 16px;
    margin-top: 16px;
    margin-bottom: 10px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 5px;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 24px 16px;
}

.section {
    margin-bottom: 24px;
    border: 1px solid var(--border);
    background: var(--surface);
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.section-title {
    background-color: var(--primary);
    color: var(--background);
    padding: 12px 16px;
    font-size: 16px;
    font-weight: 600;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.section-content {
    padding: 16px;
}

.traceback-container {
    background: var(--surface);
    border-radius: 8px;
    overflow: hidden;
}

.traceback-title {
    background-color: var(--primary);
    color: var(--background);
    padding: 12px 16px;
    font-size: 16px;
    font-weight: 600;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.frame-line {
    padding-left: 12px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
    color: var(--text);
}

.frame-filename {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
    font-weight: 600;
    color: var(--primary);
}

.center-line {
    background-color: var(--primary-dark);
    color: white;
    padding: 6px 12px;
    font-weight: 600;
    border-radius: 4px;
}

.lineno {
    margin-right: 8px;
    color: var(--text-tertiary);
    user-select: none;
}

.frame-title {
    font-weight: 500;
    padding: 12px 16px;
    background-color: var(--surface-light);
    color: var(--text);
    font-size: 14px;
    border-radius: 4px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-left: 4px solid var(--primary);
}

.collapse-btn {
    background: var(--primary);
    color: var(--background);
    border: none;
    width: 24px;
    height: 24px;
    font-size: 14px;
    cursor: pointer;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-left: 10px;
    transition: background-color 0.2s;
}

.collapse-btn:hover {
    backgroun
"""

JS = """
<script type="text/javascript">
    function collapse(element){
        const targetId = element.getAttribute("data-target-id");
        const target = document.getElementById(targetId);

        if (target.classList.contains("collapsed")){
            element.innerHTML = "&#8210;"; // Minus symbol
            target.classList.remove("collapsed");
        } else {
            element.innerHTML = "+"; // Plus symbol
            target.classList.add("collapsed");
        }
    }

    function toggleSection(sectionId) {
        const section = document.getElementById(sectionId);
        const button = document.querySelector(`[data-section="${sectionId}"]`);
        
        if (section.classList.contains("collapsed")) {
            section.classList.remove("collapsed");
            button.innerHTML = "&#8210;"; // Minus symbol
        } else {
            section.classList.add("collapsed");
            button.innerHTML = "+"; // Plus symbol
        }
    }

    document.addEventListener('DOMContentLoaded', function() {
        // Initialize all sections as expanded
        const sections = document.querySelectorAll('.section-content');
        sections.forEach(section => {
            if (section.id !== 'traceback-section') {
                section.classList.add('collapsed');
                const button = document.querySelector(`[data-section="${section.id}"]`);
                if (button) button.innerHTML = "+";
            }
        });
    });
</script>
"""
TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style type='text/css'>
            {styles}
        </style>
        <title>Nexios Debug - {error_type}</title>
    </head>
    <body>
        <div class="container">
            <div class="header-section">
                <h1>500 - Internal Server Error</h1>
                <h2>{error}</h2>
                <div class="error-id">Error ID: {error_id}</div>
                <div class="timestamp">Occurred at {timestamp}</div>
            </div>

            <!-- Traceback Section -->
            <div class="section">
                <div class="section-title">
                    <span>Traceback</span>
                    <button class="collapse-btn" data-section="traceback-section" onclick="toggleSection('traceback-section')">&#8210;</button>
                </div>
                <div id="traceback-section" class="section-content">
                    <div>{exc_html}</div>
                </div>
            </div>

            <!-- Request Information Section -->
            <div class="section">
                <div class="section-title">
                    <span>Request Information</span>
                    <button class="collapse-btn" data-section="request-section" onclick="toggleSection('request-section')">+</button>
                </div>
                <div id="request-section" class="section-content">
                    {request_info}
                </div>
            </div>

            <!-- System Information Section -->
            <div class="section">
                <div class="section-title">
                    <span>System Information</span>
                    <button class="collapse-btn" data-section="system-section" onclick="toggleSection('system-section')">+</button>
                </div>
                <div id="system-section" class="section-content">
                    {system_info}
                </div>
            </div>

            <!-- Suggestions Section -->
            <div class="section">
                <div class="section-title">
                    <span>Debugging Suggestions</span>
                    <button class="collapse-btn" data-section="suggestions-section" onclick="toggleSection('suggestions-section')">+</button>
                </div>
                <div id="suggestions-section" class="section-content">
                    {debugging_suggestions}
                </div>
            </div>

            <!-- JSON Data Section -->
            <div class="section">
                <div class="section-title">
                    <span>Error JSON Data</span>
                    <button class="collapse-btn" data-section="json-section" onclick="toggleSection('json-section')">+</button>
                </div>
                <div id="json-section" class="section-content">
                    <div class="code-box">
                        <div class="code-header">Error Data (JSON)</div>
                        <pre class="code-content">{error_json}</pre>
                    </div>
                </div>
            </div>
        </div>
        {js}
    </body>
</html>
"""
FRAME_TEMPLATE = """
<div>
    <p class="frame-title">
         File <span class="frame-filename">{frame_filename}</span>,
        line <i>{frame_lineno}</i>,
        in <b>{frame_name}</b>
        <button class="collapse-btn" data-target-id="{frame_filename}-{frame_lineno}" onclick="collapse(this)">
            {collapse_button}
        </button>
    </p>
    <div id="{frame_filename}-{frame_lineno}" class="source-code {collapsed}">{code_context}</div>
    {locals_html}
</div>
"""

LINE = """
<p><span class="frame-line">
<span class="lineno">{lineno}.</span> {line}</span></p>
"""

CENTER_LINE = """
<p class="center-line"><span class="frame-line">
<span class="lineno">{lineno}.</span> {line}</span></p>
"""


ServerErrHandlerType = typing.Callable[[Request, Response, Exception], typing.Any]


class ServerErrorMiddleware(BaseMiddleware):
    def __init__(self, handler: typing.Optional[ServerErrHandlerType] = None):
        self.handler = handler

    async def __call__(
        self,
        request: Request,
        response: Response,
        next_middleware: typing.Callable[[], typing.Awaitable[Response]],
    ) -> typing.Any:
        # Store the current request for error context
        self.current_request = request
        # Get debug mode from config
        self.debug = get_config().debug or True

        try:
            return await next_middleware()  
        except Exception as exc:
            if self.handler:
                response = await self.handler(request, response, exc)
            if self.debug:
                response = self.get_debug_response(request, response, exc)
            else:
                response = self.error_response(response)

            err = traceback.format_exc()
            logger.error(err)
            return response

    def error_response(self, res: Response):
        return res.text("Internal Server Error", status_code=500)

    def get_debug_response(
        self, request: Request, response: Response, exc: Exception
    ) -> Response:
        accept = request.headers.get("accept", "")
        if "text/html" in accept:
            content: str = self.generate_html(exc)
            return response.html(content, status_code=500)
        content = self.generate_plain_text(exc)
        return response.text(content, status_code=500)

    def format_line(
        self, index: int, line: str, frame_lineno: int, frame_index: int
    ) -> str:
        values: typing.Dict[str, typing.Any] = {
            # HTML escape - line could contain < or >
            "line": html.escape(line).replace(" ", "&nbsp"),
            "lineno": (frame_lineno - frame_index) + index,
        }

        if index != frame_index:
            return LINE.format(**values)
        return CENTER_LINE.format(**values)

    def _format_locals(self, frame_locals: typing.Dict[str, typing.Any]) -> str:
        """Format local variables for display in the error template."""
        if not frame_locals:
            return ""

        locals_html = "<div class='stack-locals'><h4>Local Variables:</h4>\n"
        for var_name, var_value in frame_locals.items():
            try:
                # Skip internal variables
                if var_name.startswith("__") and var_name.endswith("__"):
                    continue

                # Format value safely
                value_str = html.escape(repr(var_value))
                if len(value_str) > 500:  # Truncate long values
                    value_str = value_str[:500] + "..."

                locals_html += f"<div><span style='color: #f39c12;'>{html.escape(var_name)}</span> = {value_str}</div>\n"
            except Exception:
                locals_html += f"<div><span style='color: #f39c12;'>{html.escape(var_name)}</span> = <error displaying value></div>\n"

        locals_html += "</div>"
        return locals_html

    def generate_frame_html(self, frame: inspect.FrameInfo, is_collapsed: bool) -> str:
        code_context: str = "".join(  # type:ignore
            self.format_line(
                index,
                line,
                frame.lineno,
                frame.index,  # type:ignore
            )
            for index, line in enumerate(frame.code_context or [])  # type:ignore
        )

        # Format local variables if available
        locals_html = (
            self._format_locals(frame.frame.f_locals) if hasattr(frame, "frame") else ""
        )

        values: typing.Dict[str, typing.Any] = {
            "frame_filename": html.escape(frame.filename),
            "frame_lineno": frame.lineno,
            "frame_name": html.escape(frame.function),
            "code_context": code_context,
            "collapsed": "collapsed" if is_collapsed else "",
            "collapse_button": "+" if is_collapsed else "&#8210;",
            "locals_html": locals_html,
        }
        return FRAME_TEMPLATE.format(**values)

    def generate_plain_text(self, exc: Exception) -> str:
        return "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

    def _format_request_info(self, request: Request) -> str:
        """Format request information for display in the error template."""
        method = request.method
        url = str(request.url)

        # General request info
        _html = f"""
        <div class="info-grid">
            <div class="info-block">
                <h3>Request Details</h3>
                <div class="info-item">
                    <div class="info-label">Method:</div>
                    <div class="info-value">{html.escape(method)}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">URL:</div>
                    <div class="info-value">{html.escape(url)}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Path:</div>
                    <div class="info-value">{html.escape(request.path)}</div>
                </div>
                
            </div>
            
            <div class="info-block">
                <h3>Headers</h3>
                <table class="key-value-table">
        """

        # Add headers
        for name, value in request.headers.items():
            _html += f"""
                    <tr>
                        <td>{html.escape(name)}</td>
                        <td>{html.escape(value)}</td>
                    </tr>
            """

        _html += """
                </table>
            </div>
        </div>
        """

        # Add query parameters if available
        if hasattr(request, "query_params") and request.query_params:
            _html += """
            <div class="info-block">
                <h3>Query Parameters</h3>
                <table class="key-value-table">
            """

            for name, value in request.query_params.items():
                _html += f"""
                    <tr>
                        <td>{html.escape(name)}</td>
                        <td>{html.escape(str(value))}</td>
                    </tr>
                """

            _html += """
                </table>
            </div>
            """

        return _html

    def _format_system_info(self) -> str:
        """Format system information for display in the error template."""
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

        _html = f"""
        <div class="info-grid">
            <div class="info-block">
                <h3>Nexios</h3>
                <div class="info-item">
                    <div class="info-label">Nexios Version:</div>
                    <div class="info-value">{html.escape(nexios_version)}</div> 
                </div>
                <div class="info-item">
                    <div class="info-label">Debug Mode:</div>
                    <div class="info-value">{self.debug}</div>
                </div>
            </div>
            
            <div class="info-block">
                <h3>Python</h3>
                <div class="info-item">
                    <div class="info-label">Python Version:</div>
                    <div class="info-value">{html.escape(python_version)}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Python Path:</div>
                    <div class="info-value">{html.escape(sys.executable)}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Python Implementation:</div>
                    <div class="info-value">{html.escape(platform.python_implementation())}</div>
                </div>
            </div>
        </div>
        
        <div class="info-grid">
            <div class="info-block">
                <h3>System</h3>
                <div class="info-item">
                    <div class="info-label">Platform:</div>
                    <div class="info-value">{html.escape(platform.platform())}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">OS:</div>
                    <div class="info-value">{html.escape(platform.system())} {html.escape(platform.release())}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Architecture:</div>
                    <div class="info-value">{html.escape(platform.machine())}</div>
                </div>
            </div>
            
            <div class="info-block">
                <h3>Environment</h3>
                <div class="info-item">
                    <div class="info-label">Process ID:</div>
                    <div class="info-value">{os.getpid()}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Current Directory:</div>
                    <div class="info-value">{html.escape(os.getcwd())}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Python Path:</div>
                    <div class="info-value">{html.escape(str(sys.path))}</div>
                </div>
            </div>
        </div>
        """

        return _html

    def _generate_error_json(self, exc: Exception, exc_type_str: str) -> str:
        """Generate a JSON representation of the error for debugging."""
        error_data: typing.Dict[str, typing.Any] = {
            "error": {
                "type": exc_type_str,
                "message": str(exc),
                "traceback": traceback.format_exc(),
            },
            "system": {
                "nexios_version": nexios_version,
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "platform": platform.platform(),
                "debug_mode": self.debug,
            },
            "timestamp": datetime.datetime.now().isoformat(),
            "error_id": str(uuid.uuid4()),
        }

        try:
            return json.dumps(error_data, indent=2)
        except:
            # If JSON serialization fails, provide a simplified version
            return json.dumps(
                {
                    "error": {
                        "type": exc_type_str,
                        "message": str(exc),
                        "note": "Full error data could not be serialized to JSON",
                    }
                },
                indent=2,
            )

    def _generate_debugging_suggestions(self, exc: Exception, exc_type_str: str) -> str:
        """Generate debugging suggestions based on the error type."""
        suggestions: typing.List[typing.Dict[str, str]] = []

        # Common error types and suggestions
        if "ImportError" in exc_type_str or "ModuleNotFoundError" in exc_type_str:
            suggestions.append(
                {
                    "title": "Missing Module",
                    "text": "This error typically occurs when Python cannot find a required module. Check that all dependencies are installed correctly. Try running 'pip install -r requirements.txt'.",
                }
            )

        elif "SyntaxError" in exc_type_str:
            suggestions.append(
                {
                    "title": "Syntax Error",
                    "text": "There's a syntax error in your code. Check the line indicated in the traceback for mismatched parentheses, missing colons, or incorrect indentation.",
                }
            )

        elif "AttributeError" in exc_type_str:
            suggestions.append(
                {
                    "title": "Attribute Error",
                    "text": "You're trying to access an attribute or method that doesn't exist on the object. Check for typos or make sure the object is of the expected type before accessing its attributes.",
                }
            )

        elif "KeyError" in exc_type_str:
            suggestions.append(
                {
                    "title": "Key Error",
                    "text": "You're trying to access a dictionary key that doesn't exist. Make sure the key exists before trying to access it, or use dictionary.get(key) method with a default value.",
                }
            )

        elif "NameError" in exc_type_str:
            suggestions.append(
                {
                    "title": "Name Error",
                    "text": "You're trying to use a variable that hasn't been defined. Check for typos or make sure to define the variable before using it.",
                }
            )

        elif "TypeError" in exc_type_str:
            suggestions.append(
                {
                    "title": "Type Error",
                    "text": "An operation is being performed on an object of an inappropriate type. Check the types of your variables and make sure they match what the operation expects.",
                }
            )

        elif "ValueError" in exc_type_str:
            suggestions.append(
                {
                    "title": "Value Error",
                    "text": "An operation is receiving an argument with the right type but an inappropriate value. Check the value of the arguments you're passing to functions.",
                }
            )

        elif "IndexError" in exc_type_str:
            suggestions.append(
                {
                    "title": "Index Error",
                    "text": "You're trying to access an index that's out of range. Make sure the index is valid before accessing it, or use a try/except block to handle the error.",
                }
            )

        elif "FileNotFoundError" in exc_type_str:
            suggestions.append(
                {
                    "title": "File Not Found",
                    "text": "The system cannot find the file specified. Check the file path and make sure the file exists.",
                }
            )

        elif "PermissionError" in exc_type_str:
            suggestions.append(
                {
                    "title": "Permission Error",
                    "text": "You don't have permission to access the specified file or directory. Check the file permissions or run the application with higher privileges.",
                }
            )

        # Add a general debugging strategy for all errors
        suggestions.append(
            {
                "title": "General Debugging Steps",
                "text": "1. Check the traceback to find where the error occurred.<br>2. Review the variables at that point using the local variables section.<br>3. Add logging statements around the error to track variable values.<br>4. Use a debugger to step through the code execution.",
            }
        )

        # Format the suggestions as HTML
        _html = ""
        for suggestion in suggestions:
            _html += f"""
            <div class="suggestion">
                <div class="suggestion-title">{html.escape(suggestion["title"])}</div>
                <div>{suggestion["text"]}</div>
            </div>
            """

        return _html

    def generate_html(self, exc: Exception, limit: int = 7) -> str:
        """Generate an enhanced HTML page for displaying error information."""
        # Generate a unique error ID for tracking
        error_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Get exception information
        traceback_obj = traceback.TracebackException.from_exception(
            exc, capture_locals=True
        )

        # Get exception type name
        if sys.version_info >= (3, 13):
            exc_type_str = traceback_obj.exc_type_str
        else:
            exc_type_str = traceback_obj.exc_type.__name__

        # Format the error message
        error = f"{html.escape(exc_type_str)}: {html.escape(str(traceback_obj))}"

        # Generate traceback HTML
        exc_html = ""
        is_collapsed = False
        exc_traceback = exc.__traceback__
        if exc_traceback is not None:
            frames = inspect.getinnerframes(exc_traceback, limit)
            for frame in reversed(frames):
                exc_html += self.generate_frame_html(frame, is_collapsed)
                is_collapsed = True

        # Get request information if available
        try:
            request_info = self._format_request_info(
                getattr(self, "current_request", Request({}))
            )
        except Exception as e:
            request_info = f"<div class='info-block'><h3>Error retrieving request information</h3><p>{html.escape(str(e))}</p></div>"

        # Get system information
        try:
            system_info = self._format_system_info()
        except Exception as e:
            system_info = f"<div class='info-block'><h3>Error retrieving system information</h3><p>{html.escape(str(e))}</p></div>"

        # Generate debugging suggestions
        try:
            debugging_suggestions = self._generate_debugging_suggestions(
                exc, exc_type_str
            )
        except Exception as e:
            debugging_suggestions = f"<div class='info-block'><h3>Error generating debugging suggestions</h3><p>{html.escape(str(e))}</p></div>"

        # Generate JSON representation of the error
        try:
            error_json = html.escape(self._generate_error_json(exc, exc_type_str))
        except Exception as e:
            error_json = html.escape(f"Error generating JSON data: {str(e)}")

        # Put everything together in the template
        return TEMPLATE.format(
            styles=STYLES,
            js=JS,
            error=error,
            error_type=html.escape(exc_type_str),
            error_id=error_id,
            timestamp=timestamp,
            exc_html=exc_html,
            request_info=request_info,
            system_info=system_info,
            debugging_suggestions=debugging_suggestions,
            error_json=error_json,
        )

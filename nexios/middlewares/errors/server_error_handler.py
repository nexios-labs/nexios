from nexios.middlewares.base import BaseMiddleware 
from nexios.http import Request,Response
from nexios.config import get_config
import traceback,html,sys,inspect,typing
from nexios.types import HandlerType
from nexios.logging import DEBUG,create_logger
logger = create_logger(__name__,log_level=DEBUG)
STYLES = """
body {
    font-family: Arial, sans-serif;
    background-color: #1e1e1e;
    color: #eaeaea;
    margin: 20px;
    padding: 0;
}
h1 {
    color: #E67E22;
}
h2 {
    color: #f39c12;
}
.traceback-container {
    border-left: 5px solid #E67E22;
    background: #2c2c2c;
    padding: 15px;
    border-radius: 5px;
}
.traceback-title {
    background-color: #E67E22;
    color: #fff;
    padding: 12px;
    font-size: 18px;
    font-weight: bold;
    border-radius: 3px;
}
.frame-line {
    padding-left: 12px;
    font-family: monospace;
    color: #f9f9f9;
}
.frame-filename {
    font-family: monospace;
    font-weight: bold;
    color: #f39c12;
}
.center-line {
    background-color: #E67E22;
    color: #fff;
    padding: 6px 12px;
    font-weight: bold;
    border-radius: 3px;
}
.lineno {
    margin-right: 8px;
    color: #f39c12;
}
.frame-title {
    font-weight: bold;
    padding: 12px;
    background-color: #333;
    color: #eaeaea;
    font-size: 16px;
    border-radius: 5px;
    border-left: 4px solid #E67E22;
}
.collapse-btn {
    float: right;
    background: #E67E22;
    color: white;
    border: none;
    padding: 4px 8px;
    font-size: 14px;
    cursor: pointer;
    border-radius: 3px;
}
.collapse-btn:hover {
    background: #d35400;
}
.collapsed {
    display: none;
}
.source-code {
    font-family: 'Courier New', monospace;
    font-size: 14px;
    background: #282828;
    color: #f1c40f;
    padding: 10px;
    border-radius: 3px;
}
"""

JS = """
<script type="text/javascript">
    function collapse(element){
        const frameId = element.getAttribute("data-frame-id");
        const frame = document.getElementById(frameId);

        if (frame.classList.contains("collapsed")){
            element.innerHTML = "&#8210;"; // Minus symbol
            frame.classList.remove("collapsed");
        } else {
            element.innerHTML = "+"; // Plus symbol
            frame.classList.add("collapsed");
        }
    }
</script>
"""

TEMPLATE = """
<html>
    <head>
        <style type='text/css'>
            {styles}
        </style>
        <title>Nexios Debugger</title>
    </head>
    <body>
        <h1>500 - Internal Server Error</h1>
        <h2>{error}</h2>
        <div class="traceback-container">
            <p class="traceback-title">Traceback (most recent call last):</p>
            <div>{exc_html}</div>
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
        <button class="collapse-btn" data-frame-id="{frame_filename}-{frame_lineno}" onclick="collapse(this)">
            {collapse_button}
        </button>
    </p>
    <div id="{frame_filename}-{frame_lineno}" class="source-code {collapsed}">{code_context}</div>
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




class ServerErrorMiddleware(BaseMiddleware):
    def __init__(self, handler :typing.Optional[HandlerType | None]= None):
        self.handler = handler
    async def __call__(self, request :Request, response :Response, next_middleware : typing.Callable[...,typing.Awaitable[None]]):
        self.debug = get_config().debug or True
        try:
            await next_middleware()
            
        except Exception as exc:
            if self.handler:
                response =  await self.handler(request,response,exc)
            if self.debug:
                response =  self.get_debug_response(request,response,exc)
            
            else :
                response = self.error_response(response)
            
            err = traceback.format_exc()
            logger.error(err)
            return response
        
            
    def error_response(self,res :Response):
        return res.text("Internal Server Error",status_code=500)
    
    
    def get_debug_response(self, request :Request, response :Response, exc :Exception) -> Response:
        accept = request.headers.get("accept", "")
        if "text/html" in accept:
            content :str= self.generate_html(exc)
            return response.html(content, status_code=500)
        content = self.generate_plain_text(exc)
        return response.text(content, status_code=500)
    def format_line(self, index: int, line: str, frame_lineno: int, frame_index: int) -> str:
        values:typing.Dict[str,typing.Any] = {
            # HTML escape - line could contain < or >
            "line": html.escape(line).replace(" ", "&nbsp"),
            "lineno": (frame_lineno - frame_index) + index,
        }

        if index != frame_index:
            return LINE.format(**values)
        return CENTER_LINE.format(**values)
    def generate_frame_html(self, frame: inspect.FrameInfo, is_collapsed: bool) -> str:
        code_context :str = "".join( #type:ignore
            self.format_line(
                index,
                line,
                frame.lineno,
                frame.index,  #type:ignore
            )
            for index, line in enumerate(frame.code_context or []) #type:ignore
        )

        values :typing.Dict[str,typing.Any] = {
           
            "frame_filename": html.escape(frame.filename),
            "frame_lineno": frame.lineno,
            "frame_name": html.escape(frame.function),
            "code_context": code_context,
            "collapsed": "collapsed" if is_collapsed else "",
            "collapse_button": "+" if is_collapsed else "&#8210;",
        }
        return FRAME_TEMPLATE.format(**values)
    def generate_plain_text(self, exc: Exception) -> str:
        return "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    
    def generate_html(self, exc: Exception, limit: int = 7) -> str:
        traceback_obj = traceback.TracebackException.from_exception(exc, capture_locals=True)

        exc_html = ""
        is_collapsed = False
        exc_traceback = exc.__traceback__
        if exc_traceback is not None:
            frames = inspect.getinnerframes(exc_traceback, limit)
            for frame in reversed(frames):
                exc_html += self.generate_frame_html(frame, is_collapsed)
                is_collapsed = True

        if sys.version_info >= (3, 13): 
            exc_type_str = traceback_obj.exc_type_str
        else: 
            exc_type_str = traceback_obj.exc_type.__name__

       
        error = f"{html.escape(exc_type_str)}: {html.escape(str(traceback_obj))}"

        return TEMPLATE.format(styles=STYLES, js=JS, error=error, exc_html=exc_html)
            
            
                
            
            
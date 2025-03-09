from typing import (
    Union,
)

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import (
    HTMLResponse,
    FileResponse,
)

from engrave.template import get_template


def create_fastapi(
    dir_template: Union[str, Path],
    **jinja2_kwargs,
) -> FastAPI:

    fast_api = FastAPI()
    template = get_template(dir_src=dir_template)

    @fast_api.get("/{path:path}", response_class=HTMLResponse)
    async def render(request: Request, path: str):

        # Default to index.html if path is a directory-like
        if not path or path.endswith("/"):
            if path and not path.endswith("/"):
                path = path + "/"
            path = path + "index.html"

        # Use engrave.template for HTML files, otherwise serve as static file
        if path.endswith('.html'):
            try:
                return template(path).render(request=request)
            except Exception as e:
                from fastapi import HTTPException
                raise HTTPException(status_code=404, detail=f"Template error: {str(e)}")
        else:
            file_path = Path(dir_template) / path
            if file_path.exists() and file_path.is_file():
                return FileResponse(file_path)
            else:
                from fastapi import HTTPException
                raise HTTPException(status_code=404, detail=f"File not found: {path}")

    return fast_api

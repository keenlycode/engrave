import typer
import uvicorn
from pathlib import Path
from typing import List
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from engrave.template import get_template

app = typer.Typer(help="Static website generator with live preview")
_global_dir_src = None  # Will store the template source directories

def create_app(dir_src):
    """Create FastAPI app configured to serve templates from dir_src"""
    fastapi_app = FastAPI(title="Engrave Preview Server")

    # Configure the template engine
    template = get_template(dir_src=dir_src)

    # Mount static directories if they exist
    for directory in dir_src if isinstance(dir_src, list) else [dir_src]:
        directory = Path(directory)
        static_dir = directory / "static"
        if static_dir.exists() and static_dir.is_dir():
            fastapi_app.mount(
                "/static",
                StaticFiles(directory=str(static_dir)),
                name=f"static_{static_dir}"
            )

    @fastapi_app.get("/{path:path}", response_class=HTMLResponse)
    async def render(request: Request, path: str = ""):
        try:
            # Handle root path
            if not path or path.endswith('/'):
                template_path = f"{path}index.html" if path else "index.html"
            # Handle HTML extensions
            elif not path.endswith('.html'):
                template_path = f"{path}.html"
            else:
                template_path = path

            return template(template_path).render()
        except Exception as e:
            return HTMLResponse(
                content=f"""
                <h1>Template Error</h1>
                <pre>{str(e)}</pre>
                """,
                status_code=500
            )

    return fastapi_app

@app.command()
def serve(
    dir_src: List[Path] = typer.Argument(
        ...,
        help="Directory or directories containing template files",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    host: str = typer.Option("127.0.0.1", help="Host address to bind"),
    port: int = typer.Option(8000, help="Port to bind"),
    reload: bool = typer.Option(True, help="Enable auto-reload on template changes")
):
    """
    Start a development server that renders templates from the specified directories
    """
    global _global_dir_src
    _global_dir_src = dir_src

    print(f"Starting Engrave server with template directories: {', '.join(str(d) for d in dir_src)}")
    print(f"Server running at http://{host}:{port}")
    print("Press CTRL+C to stop")

    if reload:
        # When reload=True, we need to pass the app factory to uvicorn
        # This allows it to recreate the app on file changes
        uvicorn.run(
            "engrave.cli:get_app",
            host=host,
            port=port,
            reload=True,
            reload_dirs=[str(d) for d in dir_src]
        )
    else:
        # Create the app directly and run it
        fastapi_app = create_app(dir_src)
        uvicorn.run(fastapi_app, host=host, port=port)

def get_app():
    """
    Factory function to create the FastAPI app
    This is used by uvicorn when reload=True
    """
    global _global_dir_src
    if _global_dir_src is None:
        raise RuntimeError("App not initialized properly")
    return create_app(_global_dir_src)

def main():
    """Entry point for the CLI application"""
    app()

if __name__ == "__main__":
    main()

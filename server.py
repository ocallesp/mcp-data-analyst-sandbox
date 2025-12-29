import os
import sys
import io
import json
from contextlib import redirect_stdout
from typing import Dict, Any, List

from fastmcp import FastMCP
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

DATA_DIR = "/app/data"
PLOTS_DIR = "/app/plots"

mcp = FastMCP(
    name="Data Analyst Sandbox",
    instructions="Secure Python execution environment for data analysis",
    version="2025.12"
)

@mcp.tool
def execute_python_code(code: str) -> dict:
    """Execute Python code in a restricted environment"""
    # Allow some safe builtins
    safe_builtins = {
        "len": len,
        "range": range,
        "print": print,
        "int": int,
        "float": float,
        "str": str,
        "list": list,
        "dict": dict,
        "set": set,
        "tuple": tuple,
        "enumerate": enumerate,
        "zip": zip,
        "min": min,
        "max": max,
        "sum": sum,
    }
    
    namespace: Dict[str, Any] = {
        "pd": pd,
        "np": np,
        "plt": plt,
        "os": os,
        "DATA_DIR": DATA_DIR,
        "PLOTS_DIR": PLOTS_DIR,
        "__builtins__": safe_builtins,
    }

    output = io.StringIO()
    try:
        # Clear previous plots to ensure we only return new ones
        for f in os.listdir(PLOTS_DIR):
            file_path = os.path.join(PLOTS_DIR, f)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception:
                pass

        with redirect_stdout(output):
            exec(code, namespace, namespace)

        # Find newly created plots
        plots = [
            f"http://localhost:8765/plots/{f}"
            for f in os.listdir(PLOTS_DIR)
            if f.endswith(('.png', '.jpg', '.jpeg'))
        ]

        return {
            "output": output.getvalue(),
            "plots": plots,
            "success": True
        }

    except Exception as e:
        return {
            "output": None,
            "error": f"{type(e).__name__}: {str(e)}",
            "success": False
        }

# Plot serving endpoint (using the underlying Starlette app)
from starlette.responses import FileResponse, JSONResponse
@mcp.http_app().route("/plots/{filename}")
async def serve_plot(request):
    filename = request.path_params["filename"]
    file_path = os.path.join(PLOTS_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return JSONResponse({"error": "File not found"}, status_code=404)

if __name__ == "__main__":
    # Use HTTP transport to allow plot serving via the same port
    mcp.run(transport="http", host="0.0.0.0", port=8765)
    
    uvicorn.run(app, host="0.0.0.0", port=8765)

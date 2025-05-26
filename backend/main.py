# main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
import subprocess
import os
import json
from var_extractor import is_code_safe, extract_variables_from_code

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/run")
async def run_code(request: Request):
    data = await request.json()
    code = data.get("code", "")

    if not is_code_safe(code):
        return JSONResponse({
            "stdout": "",
            "stderr": "Error: Use of imports, function calls, or unsafe code is blocked.",
            "variables": {}
        })

    try:
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".py", delete=False) as tmp:
            vars_path = tmp.name + ".vars.json"

            # ✅ Write user's code FIRST
            tmp.write(code + "\n")

            # ✅ THEN append variable capture logic
            tmp.write("import json\n")
            tmp.write("try:\n")
            tmp.write("    __output_vars__ = {}\n")
            tmp.write("    for k, v in dict(locals()).items():\n")
            tmp.write("        if not k.startswith('__') and not callable(v):\n")
            tmp.write("            try:\n")
            tmp.write("                json.dumps(v)\n")
            tmp.write("                __output_vars__[k] = v\n")
            tmp.write("            except:\n")
            tmp.write("                pass\n")
            tmp.write(f"    with open(r'{vars_path}', 'w') as f:\n")
            tmp.write("        f.write(json.dumps(__output_vars__))\n")
            tmp.write("except Exception as e:\n")
            tmp.write(f"    with open(r'{vars_path}', 'w') as f:\n")
            tmp.write("        f.write(json.dumps({\"__error__\": str(e)}))\n")

            tmp.flush()
            tmp_path = tmp.name

        result = subprocess.run(
            ["python", tmp_path],
            capture_output=True,
            text=True,
            timeout=2
        )

        stdout = result.stdout
        stderr = result.stderr

        if os.path.exists(vars_path):
            with open(vars_path, "r") as f:
                try:
                    vars_dict = json.load(f)
                except Exception as e:
                    vars_dict = {"__error__": f"Failed to parse vars.json: {e}"}
            os.remove(vars_path)
        else:
            vars_dict = {}

    except subprocess.TimeoutExpired:
        stdout = ""
        stderr = "Error: Code execution timed out"
        vars_dict = {}
    except Exception as e:
        stdout = ""
        stderr = f"Error: {e}"
        vars_dict = {}
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return JSONResponse({
        "stdout": stdout,
        "stderr": stderr,
        "variables": vars_dict
    })

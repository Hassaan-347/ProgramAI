import subprocess
import tempfile
import os


def run_python(code):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
        f.write(code.encode())
        filename = f.name

    try:
        result = subprocess.run(
            ["python3", filename],
            capture_output=True,
            text=True,
            timeout=5
        )

        return result.stdout, result.stderr

    finally:
        os.remove(filename)


def run_cpp(code):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".cpp") as f:
        f.write(code.encode())
        cpp_file = f.name

    exe_file = cpp_file.replace(".cpp", "")

    try:
        compile_result = subprocess.run(
            ["g++", cpp_file, "-o", exe_file],
            capture_output=True,
            text=True
        )

        if compile_result.returncode != 0:
            return "", compile_result.stderr

        run_result = subprocess.run(
            [exe_file],
            capture_output=True,
            text=True,
            timeout=5
        )

        return run_result.stdout, run_result.stderr

    finally:
        if os.path.exists(cpp_file):
            os.remove(cpp_file)
        if os.path.exists(exe_file):
            os.remove(exe_file)


def run_code(language, code):
    if language == "python":
        return run_python(code)
    elif language == "cpp":
        return run_cpp(code)
    else:
        return "", f"Execution not supported for {language}"

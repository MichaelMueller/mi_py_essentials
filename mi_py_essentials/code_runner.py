from typing import Dict, Optional, Tuple
import sys, subprocess, os, tempfile, asyncio, shutil, zipfile, aiofiles, shlex
from pathlib import Path
import aiofiles.os
# pip
import pydantic
# local
from .function import Function

class CodeRunner(Function):
    
    class Args(pydantic.BaseModel):
        code_or_script_path: str = None,
        args: list[str] = None,
        venv_path: str = None

    def __init__(self, args:Args):
        super().__init__()
        self._args = args
        
    async def exec(self) -> tuple[str, str, int]:
        ''' Run Python code or a Python script in a subprocess, optionally within a virtual environment. '''
        if await aiofiles.os.path.exists(self._args.code_or_script_path):
            code = None
            script_path = self._args.code_or_script_path
        else:
            code = self._args.code_or_script_path
            script_path = None
        
        args = self._args.args
        if args is None:
            args = []

        # 1) Decide whether we are running inline code or a script.
        if code:
            if os.name == "nt":
                # Windows
                # We must be careful to escape any double quotes in the code itself:
                escaped_code = code.replace('"', '\\"')
                command = f'python -c "{escaped_code}"'
            else:
                # Unix-like
                command = f"python -c {shlex.quote(code)}"
        else:
            # We'll call Python with a script path, plus extra args.
            cmd_args = " ".join(shlex.quote(arg) for arg in args)
            command = f"python {shlex.quote(script_path)}"
            if cmd_args:
                command += f" {cmd_args}"

        venv_path = self._args.venv_path
        # 2) If a virtual environment is specified, activate it before the command.
        #    On UNIX-like systems, we can do: source {venv_path}/bin/activate
        #    On Windows, you'd adapt to: {venv_path}\\Scripts\\activate.bat && ...
        if venv_path:
            # Convert to absolute path, just in case
            
            if os.name == "nt":
                venv_activate = Path(venv_path).joinpath("Scripts", "activate.bat")
            else:
                venv_activate = Path(venv_path).joinpath("bin", "activate")
            if not venv_activate.is_file():
                raise FileNotFoundError(f"Could not find 'activate' script in {venv_activate}")
            # Prepend the source/activate step:
            
            if os.name == "nt":
                command = 'chcp 65001 > nul 2>&1 && "' + str(venv_activate).replace('"', '\\"') + '" && '+command
            else:
                command = f"source {shlex.quote(str(venv_activate))} && {command}"

        # 3) Run the command in a subprocess shell.
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=os.environ.copy(),  # You can also supply a custom env if needed
        )

        stdout_data, stderr_data = await process.communicate()
        stdout_text = str(stdout_data.decode())
        stderr_text = str(stderr_data.decode())
        return stdout_text, stderr_text, process.returncode

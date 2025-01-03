from typing import Dict, Optional, Tuple
import sys, subprocess, os, tempfile, asyncio, shutil, zipfile
# pip
import pydantic
# local
from .function import Function

class VenvCreator(Function):
    
    class Args(pydantic.BaseModel):
        venv_path:str=".venv"
        requirements_file:Optional[str]
        no_cache:Optional[bool]=False

    def __init__(self, args:Args):
        super().__init__()
        self._args = args
        
    async def exec(self) -> None:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._exec_sync)
        
    def _exec_sync(self) -> str:
            
        # Create a temporary directory
        venv_path = self._args.venv_path
        os.makedirs( venv_path, exist_ok=True )

        # Create the virtual environment
        subprocess.check_call([sys.executable, '-m', 'venv', venv_path])

        # Determine the platform-independent path to the py exe
        py_venv_exe = os.path.join(
            venv_path, 'Scripts' if os.name == 'nt' else 'bin', 'python.exe' if os.name == 'nt' else 'python'
        )

        # Upgrade pip to the latest version
        subprocess.check_call([py_venv_exe, '-m', 'pip', 'install', '--upgrade', 'pip'])

        # Check if the requirements file exists
        requirements_file = self._args.requirements_file
        if requirements_file != None:
            if not os.path.exists(requirements_file):
                raise FileNotFoundError(f"The requirements file '{requirements_file}' does not exist.")
            
            # Install requirements from requirements.txt
            args = [py_venv_exe, '-m', 'pip', 'install']
            if self._args.no_cache:
                args.append('--no-cache-dir')
            args.extend(['-r', requirements_file])
            subprocess.check_call(args)

from typing import Dict, Optional
import sys, subprocess, os, tempfile, asyncio, shutil, zipfile, logging
# pip
import pydantic
# local
from .function import Function
from .venv_creator import VenvCreator

class Packager(Function):
    
    class Args(pydantic.BaseModel):
        output_zip:str
        requirements_file:Optional[str]=None
        additional_files:Dict[str, str]={}
        temp_dir_path:Optional[str]=None
        minpy:Optional[tuple]=None

    def __init__(self, args:Args):
        super().__init__()
        self._args = args
        
    async def exec(self) -> str:
        loop = asyncio.get_event_loop()
        output_zip = await loop.run_in_executor(None, self._exec_sync)
        return output_zip
        
    def _exec_sync(self) -> str:
        
        temp_dir:tempfile.TemporaryDirectory = None
        
        try:
            # check version
            if self._args.minpy != None:            
                """Check if the current Python version matches the required version."""
                current_version = sys.version_info[:2]
                assert current_version >= self._args.minpy, f"Error: Python {self._args.minpy[0]}.{self._args.minpy[1]} or higher is required."
                
            # Create a temporary directory if needed
            temp_dir_path = self._args.temp_dir_path
            if temp_dir_path is None:
                temp_dir = tempfile.TemporaryDirectory()
                temp_dir_path = temp_dir.name
            else:
                temp_dir_path = os.path.abspath( temp_dir_path)
                os.makedirs( temp_dir_path, exist_ok=True )
                
            # create Venv
            venv_path = os.path.join(temp_dir_path, '.venv')
            asyncio.run( VenvCreator( VenvCreator.Args( venv_path=venv_path, requirements_file=self._args.requirements_file ) ).exec() )

            # Copy additional files/folders to their target locations in the zip directory
            logging.debug(f"Copying additional files to the virtual environment at '{venv_path}'...")
            additional_files = self._args.additional_files
            for source, target in additional_files.items():
                target_path = os.path.join(temp_dir_path, target)
                if os.path.exists(source):
                    if os.path.isdir(source):
                        shutil.copytree(source, target_path, dirs_exist_ok=True)
                    else:
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        shutil.copy2(source, target_path)
                else:
                    print(f"Warning: Source '{source}' does not exist and will be skipped.")

            # Remove unnecessary files to make the environment minimal
            logging.debug(f"Cleaning up the virtual environment at '{venv_path}'...")
            cleanup_paths = [
                os.path.join(venv_path, 'lib', 'python*.*/__pycache__'),
                os.path.join(venv_path, 'share'),
                os.path.join(venv_path, 'include'),
                os.path.join(venv_path, 'bin', '*.exe') if os.name == 'nt' else os.path.join(venv_path, 'bin', '*.pyo')
            ]

            for path in cleanup_paths:
                if os.path.exists(path):
                    shutil.rmtree(path, ignore_errors=True)

            # Additional cleanup: remove unnecessary files
            for root, _, files in os.walk(venv_path):
                for file in files:
                    if file.endswith(('.pyc', '.pyo', '.dist-info')):
                        file_path = os.path.join(root, file)
                        os.remove(file_path)

            # Create a zip file of the .venv directory
            output_zip = self._args.output_zip
            output_dir = os.path.dirname(output_zip)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            logging.debug(f"Packaging minimal virtual environment into '{output_zip}'...")
            with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, start=temp_dir_path)
                        zipf.write(file_path, arcname=arcname)

            logging.info(f"Minimal virtual environment packaged into '{output_zip}'.")
        finally:
            if temp_dir:
                temp_dir.cleanup()
        
        
        return self._args.output_zip
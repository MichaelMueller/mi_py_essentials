# built-in
import asyncio, sys
# local
from .test import Test
from .code_runner import CodeRunner

class CodeRunnerTest(Test):
    def __init__(self, parent:"Test") -> None:
        super().__init__(parent)
        
    async def _exec(self) -> None:
        my_version = str(sys.version)
        
        runner = CodeRunner( CodeRunner.Args(code_or_script_path="import sys; print( sys.version)") )
        
        stdout_text, stderr_text, returncode = await runner.exec()
        
        self._print(f"stdout_text: {stdout_text.strip()}")
        self._print(f"stderr_text: {stderr_text.strip()}")
        self._check( returncode==0, f"returncode==0, got {returncode}" )
        self._check( stdout_text.strip()==my_version.strip(), f"stdout_text=={my_version}, got {stdout_text}" )
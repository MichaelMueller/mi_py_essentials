class PyBootLoader:

    def exec(script_or_code:str, minpy:tuple=(3,10), venv_dir:str="venv", req_file="requirements.txt") -> None:
        import sys
        
        """Check if the current Python version matches the required version."""
        current_version = sys.version_info[:2]
        if current_version < minpy:
            print(f"Error: Python {minpy[0]}.{minpy[1]} or higher is required.")
            sys.exit(1)

        import os, subprocess
        """Create a virtual environment if it doesn't already exist."""
        if not os.path.exists(venv_dir):
            print(f"Creating virtual environment in '{venv_dir}'...")
            subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
            """Install requirements from requirements.txt."""
            if os.path.exists(req_file):
                print(f"Installing dependencies from '{req_file}'...")
                pip_executable = os.path.join(venv_dir, "bin", "pip") if os.name != "nt" else os.path.join(venv_dir, "Scripts", "pip.exe")
                subprocess.check_call([pip_executable, "install", "-r", req_file])
                
        else:
            print(f"Virtual environment '{venv_dir}' already exists.")
            
            """Activate the virtual environment and run the specified script."""
            python_executable = os.path.join(venv_dir, "bin", "python") if os.name != "nt" else os.path.join(venv_dir, "Scripts", "python.exe")

            is_script = os.path.exists(script_or_code)
                
            if is_script:
                subprocess.check_call([python_executable, script_or_code])
            else:
                subprocess.check_call([python_executable, "-c", script_or_code])
                
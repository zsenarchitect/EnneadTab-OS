import subprocess

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running command: {command}")
        print(e)

def setup_venv():
    # Activate virtual environment and upgrade pip and wheel
    run_command('.venv\\Scripts\\activate && python.exe -m pip install --upgrade pip && pip install --upgrade wheel')
    
    # Install requirements
    run_command('.venv\\Scripts\\activate && pip install -r requirements.txt')

if __name__ == "__main__":
    setup_venv()

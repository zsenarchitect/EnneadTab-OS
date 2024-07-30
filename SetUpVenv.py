import subprocess

# Activate the virtual environment and install requirements
commands = [
    '.venv\\Scripts\\activate',
    'python.exe -m pip install --upgrade pip',
    'pip install --upgrade wheel', # need this to make sure some module in requirement can install with pip(such as playsound)
    'pip install -r requirements.txt'
]


def setup_venv():
    # Run the commands in the terminal
    for command in commands:
        subprocess.run(command, shell=True, check=True)

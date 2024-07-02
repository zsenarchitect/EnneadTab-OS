import subprocess

# Activate the virtual environment and install requirements
commands = [
    'cd C:\\Users\\szhang\\github\\EnneadTab-OS',
    '.venv\\Scripts\\activate',
    'pip install -r requirements.txt'
]


def setup_venv():
    # Run the commands in the terminal
    for command in commands:
        subprocess.run(command, shell=True, check=True)

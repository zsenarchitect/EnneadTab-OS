import subprocess

# Activate the virtual environment and install requirements
commands = [
    'git config --global user.name "Sen Zhang"',
    'git config --global user.email zsenarchitect@gmail.com'
]


def setup_venv():
    # Run the commands in the terminal
    for command in commands:
        subprocess.run(command, shell=True, check=True)

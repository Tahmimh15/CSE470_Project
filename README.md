# CSE470_Project
This is the project we did for CSE470: Software Engineering. Our project is called Nimontron, and it is an event management system that to allow its users to create events, and manage invitations and tickets.

To use this project, first set up a virtual environment 


## Set up virtual environment

```
python -m venv /path/to/directory

```
Use python3 for Unix/MacOS

Next, activate the env, activating command depends on the os being used


## Activation

On Unix or MacOS, using the bash shell: ```source /path/to/venv/bin/activate```
On Unix or MacOS, using the csh shell: ```source /path/to/venv/bin/activate.csh```
On Unix or MacOS, using the fish shell: ```source /path/to/venv/bin/activate.fish```
On Windows using the Command Prompt: ```path\to\venv\Scripts\activate.bat```
On Windows using PowerShell: ```path\to\venv\Scripts\Activate.ps1```

Then, install all the required modules


## Requirements

```
pip install flask
pip install flask-login
pip install flask-migrate
pip install flask-sqlalchemy
pip install mysqlclient
pip install mysql-connector-python

```

use pip3 for Unix/MacOS


## Migrate the databases

```
flask db init
flask db migrate
flask db upgrade

```


Clone the repository in the new env to run it

```
https://github.com/Tahmimh15/CSE470_Project.git

```

Finally to use the project, run this in the terminal


## Run

```
flask run

```
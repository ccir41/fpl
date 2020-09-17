# fpl

fantasy premire legue standings scrapper
**find top gameweek scorers of your leagues**

# Getting started

**go to your terminal and type following commands**

`$ git clone https://github.com/ccir41/fpl`
`$ cd fpl`

## Create a .env file for storing your email and password

_create .env file in project dir and enter following variables values_
`$ EMAIL='youremail@email.com'`
`$ PASSWORD='yourpassword'`

### Download chrome driver for your respective operation system and chrome version from following link

_https://chromedriver.chromium.org/downloads_

###for 85.0.4183.87 chrome version

_https://chromedriver.storage.googleapis.com/index.html?path=85.0.4183.87/_

- I have included the chrome driver for ubuntu and chrome version 85.

### Create virtual environment and install requirements

> For ubuntu
> `$ python3 -m venv fplvenv`
> `$ source fplvenv/bin/activate`
> `$ pip3 install -r requirements.txt`

> For Windows
> `$ py -m venv fplvenv`
> `$ fplvenv\Scripts\activate.bat`
> `$ pip install -r requirements.txt`

### Running program

`$ python script.py`

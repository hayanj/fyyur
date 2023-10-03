# fyyur: Artist Booking Site

Fyyur is a musical venue and artist booking site that facilitates the discovery and bookings of shows between local performing artists and venues. This site lets you list new artists and venues, discover them, and list shows with artists as a venue owner.


## Getting Started


### Pre-requisites and Local Development


Developers who wishes to work on this project should already have Python3, pip, HTML, CSS, and Javascript with Bootstrap 3 installed.

#### Backend

Tech stack includes:
* virtualenv as a tool to create isolated Python environments
* SQLAlchemy ORM to be our ORM library of choice
* PostgreSQL as our database of choice
* Python3 and Flask as our server language and server framework
* Flask-Migrate for creating and running schema migrations
* From the backend folder, you can download and install the dependencies mentioned above using pip as:
```bash
pip install virtualenv
pip install SQLAlchemy
pip install postgres
pip install Flask
pip install Flask-Migrate
```

To run this application, run the following commands:
```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

* ```bash export FLASK_APP=flaskr ``` this command will insure that Flask is going to use __init__.py in our flaskr folder.
* ```bash export FLASK_ENV=development ``` this command will insure that we will be working in development mode, which will show us an interactive debugger in the console and resart the server whenever a change is made.
* ```bash flask run ``` this command will start the application.

The application is run on http://127.0.0.1:5000/ by default and is a proxy in the frontend configuration.

#### Frontend

To install Bootstrap 3, from frontend folder run:
```bash
npm init -y
npm install bootstrap@3
```

From the frontend folder, run 
```bash
npm install // only once to install dependencies
npm start 
```

By default, the frontend will run on  http://127.0.0.1:3000/.

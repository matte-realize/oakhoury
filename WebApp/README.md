# OAKhouryTreesApp

Secret admin dashbaord available via /admin (only if you are signed in as an organization member)

## How to run the app

### Running the Flask API

- Change /python-api/.env.example to /python-api/.env . Ensure the port points to the docker instance.
- CD to /python-api and run "python -m venv venv"
- Depending on your os, run the following commands:
  - Windows: "venv\Scripts\activate"
  - MacOS/Linux: "source venv/bin/activate"
- Run "pip install -r requirements.txt"
- Run "python app.py" to start the Flask server

### Running the SvelteKit App

- Change .env.example to .env . Choose if you want passwords hashed (If you set it to false, you can sign into the accounts created in DML.sql). JWT secret can be any string
- run "npm install" to install the dependencies
- run "npm run dev" to start the SvelteKit server
- Open your browser and go to http://localhost:5173 to view
- If you click one of the buttons and you get ECONREFUSED, ensure the python app is started and pointing to the correct port specified in /pyhton-api/.env .

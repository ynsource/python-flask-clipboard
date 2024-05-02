# Clipboard (Web and API Project) with Python/Flask

This is an example project to use [Flask](https://flask.palletsprojects.com) for web backend and API service.

## Warning
This is an example project. Using this project in production is not recommended. Should be added more security mechanisms like verifying e-mail when signing up.

## Free Hosting
You can get a free [PythonAnyWhere](https://pythonanywhere.com) account. Then you can upload and test your Python web projects in there.

## To Run

You must installed Flask before via Python's pip or manually.
```
pip install flask
```

Then in root folder of this project open a terminal and type:
```
flask --app website/app run --debug
```

This will start project with default port 5000 in localhost and then you can visit `http://127.0.0.1:5000` in any web browser (Chrome, Edge, etc.)

To change port you can add --port parameter before run.
```
flask --app website/app --port 80 run
```

For production server you should NOT use --debug parameter, but in local debug mode is easy to see errors when occured and changes in project files will be automatically handled.

# License
The Unlicense. Feel free to use or change it how you need.

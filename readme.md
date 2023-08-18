# Local Development Run
- Open Terminal and execute the following command to create the virtual environment "python -m venv .venv"
- Enter into the virtual environment using command: ".\.venv\Scripts\activate"
- Install the required python libraries using command: "pip install -r requirements.txt"
- Run the command "python app.py" to start the application

# Folder Structure

- `db_directory` has the sqlite DB. The path of the file can be adjusted in  ``application/config.py`.
- `application` contains the application code
- `static` - default `static` files folder. It serves at '/static' path to store files, images and css
- `static/dashboard.css` Custom CSS. You can edit it. Its empty currently
- `templates` - Default flask templates folder
The project structure is shown below:
.
└── Project Folder
    ├── docs
    │   └── report.pdf
    ├── application
    │   ├── config.py
    │   ├── controllers.py
    │   ├── database.py
    │   ├── forms.py
    │   └── models.py
    ├── db_directory
    │   └── blogdb.sqlite3
    ├── static (contains images, css and js files)
    ├── templates (contains all HTML files)
    ├── app.py
    ├── requirements.txt
    └── readme.md





# Frontend Setup (React + Vite + Tailwind)

## Navigate to the Frontend Folder

Assuming you are in the `backend/` folder, go up one level (or directly open a new terminal):

```sh
cd  frontend
```

If the frontend folder has a subfolder for the React project (e.g., `my-react-app`), navigate into that folder:

```sh
cd my-react-app 
```
# In our case we dont , so follow the step below without moving to any sub-folder

## Install Node Dependencies

Run the following command to install dependencies:

```sh
npm install
```

(Use `yarn` or `pnpm` if that’s your team’s preference.)

## Run the Development Server

Start the development server with:

```sh
npm run dev
```

By default, Vite serves the React app on [http://127.0.0.1:5173](http://127.0.0.1:5173).

---

## Project Structure

```
frontend/
  ├── public/              # Static assets
  ├── src/                 # Source code
  │   ├── assets/          # Images, fonts, etc.
  │   ├── App.jsx          # Main application component
  │   ├── App.css          # Global styles (Tailwind included)
  │   ├── main.jsx         # React root component
  │   ├── index.css        # Additional global styles
  ├── .gitignore           # Files to ignore in git
  ├── package.json         # Dependencies and scripts
  ├── vite.config.js       # Vite configuration
  ├── tailwind.config.js   # Tailwind configuration
  ├── postcss.config.js    # PostCSS configuration
  ├── README.md            # Project documentation
```

---

## Tailwind CSS Configuration

Tailwind CSS is already set up in this project. If needed, modify `tailwind.config.js` to customize your styles.

---

## Building for Production

To build the project for production, run:

```sh
npm run dev
```

The output files will be generated in the `dist/` directory.





# Django Project Setup

## Navigate to the Backend Folder

Assuming you’re in the root directory of the project, move to the backend folder:
```sh
cd backend
```

## Create and Activate a Virtual Environment
Ensure you have Python installed, then run:
```sh
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows
```

## Install Dependencies
Install the required Python packages:
```sh
pip install -r requirements.txt
```

## Apply Migrations
Before running the server, apply the database migrations:
```sh
python manage.py migrate
```

## Create a Superuser (Optional)
To access the Django admin panel, create a superuser:
```sh
python manage.py createsuperuser
```
Follow the prompts to set up your admin credentials.

## Run the Development Server
Start the Django server:
```sh
python manage.py runserver
```
By default, the server runs at `http://127.0.0.1:8000/`.

## Project Structure
```
backend/
  ├── django404/           # Main Django project folder
  │   ├── __init__.py      # Python package indicator
  │   ├── asgi.py          # ASGI configuration
  │   ├── settings.py      # Project settings
  │   ├── urls.py          # URL routing
  │   ├── wsgi.py          # WSGI configuration
  ├── myapp/               # Django application
  │   ├── migrations/      # Database migrations
  │   ├── admin.py         # Admin panel configuration
  │   ├── apps.py          # App configuration
  │   ├── models.py        # Database models
  │   ├── serializers.py   # API serializers
  │   ├── tests.py         # Test cases
  │   ├── urls.py          # App-specific URL routing
  │   ├── views.py         # Application views
  ├── db.sqlite3           # SQLite database (default)
  ├── manage.py            # Django management script
```

## API Testing (Optional)
If using Django REST Framework, you can test API endpoints via:
- `http://127.0.0.1:8000/api/`
- Using tools like [Postman](https://www.postman.com/) or `curl`

## Deployment
To deploy the Django application, consider platforms like:
- Heroku
- DigitalOcean
- AWS EC2
- Railway

Example deployment on Heroku:
```sh
heroku create
heroku config:set DJANGO_SETTINGS_MODULE=django404.settings
heroku addons:create heroku-postgresql:hobby-dev
```

## License
This project is open-source and available under the MIT License.

---

### Happy Coding! 🚀












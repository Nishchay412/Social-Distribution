# Setting Up the PostgreSQL Database and Django Project

## 1. Install Dependencies

### PostgreSQL
Download and install PostgreSQL from the [official website](https://www.postgresql.org/download/).

### Python Dependencies
Activate your virtual environment and install the PostgreSQL adapter:

```bash
pip install psycopg2-binary
```

## 2. Create the PostgreSQL Database and User

### Open the PostgreSQL Shell
Log in as the superuser (usually `postgres`):

```bash
psql -U postgres
```

### Create the User "404group"
At the `psql` prompt, run:

```sql
CREATE USER "404group" WITH PASSWORD 'postgres';
```

### Create the Database "verdigris"
Create the database and assign ownership to the new user:

```sql
CREATE DATABASE verdigris OWNER "404group";
```

### Verify the Setup
List your databases to confirm:

```sql
\l
```

### Exit the PostgreSQL Shell
Type:

```sql
\q
```

## 3. Configure Django to Use PostgreSQL

### Update `settings.py`
In your Django project's `settings.py` file, update the `DATABASES` section:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'verdigris',       # New database name
        'USER': '404group',        # PostgreSQL user
        'PASSWORD': 'postgres',    # Password for 404group
        'HOST': 'localhost',       # Database host
        'PORT': '5432',            # Default PostgreSQL port
    }
}
```

### Apply Migrations
Run the following command to create your database schema:

```bash
python manage.py migrate
```

## 4. Run and Test the Application

### Start the Django Development Server
Launch the server with:

```bash
python manage.py runserver
```

Visit [http://localhost:8000](http://localhost:8000) in your browser to verify the application is working.

### (Optional) Data Migration
If you are migrating from another database (e.g., SQLite), you can dump and load your data:

- **Dump the data:**

  ```bash
  python manage.py dumpdata > data.json
  ```

- **Load the data into PostgreSQL:**

  ```bash
  python manage.py loaddata data.json
  ```

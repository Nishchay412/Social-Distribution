|ccid|name|
|---|---|
|riyasat|Riyasat Zaman|
|clbao|Christine Bao|
|qingqiu|Steve Tan|
|nranjan|Nishchay Ranjan|
|lin19|Yicheng Lin|






# Frontend Setup (React + Vite + Tailwind)

## Navigate to the Frontend Folder

Assuming you are in the `backend/` folder, go up one level (or directly open a new terminal):

```sh
cd ../frontend
```

If the frontend folder has a subfolder for the React project (e.g., `my-react-app`), navigate into that folder:

```sh
cd my-react-app
```

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
npm run build
```

The output files will be generated in the `dist/` directory.



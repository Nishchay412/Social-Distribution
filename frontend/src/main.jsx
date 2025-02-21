import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.jsx';
import Signup from './authentication/Signup';
import { Dashboard } from './dashboard/dashboard';
import Login from './authentication/Login';
import { User_Profile } from './dashboard/user_profile';
import { Friend_Profile } from './dashboard/friend_user_profile';
import AuthorList from './posting/AuthorList';
import EditPost from './posting/EditPost';
import UserPosts from './posting/UserPosts';

import CreatePost from './posting/CreatePost';
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
  },
  {
    path: "/sign-up",
    element: <Signup />,
  },
  {
    path: "/login",
    element: <Login/>,
  },
  {
    path: "/dashboard",
    element: <Dashboard/>,
  },
  {
    path: "/profile",
    element: <User_Profile/>,
  },
  {
    path: "/profile/:username",  // ✅ Dynamic Route for User Profile
    element: <Friend_Profile/>
  },
  {
    path: "/authorlist",  // ✅ Dynamic Route for User Profile
    element: <AuthorList/>
  },
  {
    path: "/createpost",  // ✅ Dynamic Route for User Profile
    element: <CreatePost/>
  },
  {
    path: "/posts/:id/edit",
    element: <EditPost/>
},
{
  path: "/posts/:username",
  element: <UserPosts/>
}

]);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={router} />  {/* ✅ Correctly rendering RouterProvider */}
  </StrictMode>
);

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
import MyPosts from './posting/Personalposts';
import CreatePost from './posting/CreatePost';
import PublicPosts from './posting/publicposts';
import { Header } from './dashboard/header';
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
    element: <Login />,
  },
  {
    path: "/dashboard",
    element: <Dashboard />,
  },
  {
    path: "/profile",
    element: <User_Profile />,
  },
  {
    path: "/profile/:username",  // ✅ Dynamic Route for Friend's Profile
    element: <Friend_Profile />,
  },
  {
    path: "/authorlist",
    element: <AuthorList />,
  },
  {
    path: "/createpost",
    element: <CreatePost />,
  },
  {
    path: "/posts/:postId/edit",  // ✅ Fixed to match backend expectations
    element: <EditPost />,
  },
  {
    path: "/posts/:username",
    element: <UserPosts/>,
  },
  {
    path: "/my-posts",  // ✅ Cleaner URL for user's posts
    element: <MyPosts />,
  },
  {
    path: "/publicposts",  // ✅ Cleaner URL for user's posts
    element: <PublicPosts />,
  },
  {
    path: "/Header",  // ✅ Cleaner URL for user's posts
    element: <Header/>,
  },
  
]);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={router} />  {/* ✅ Correctly rendering RouterProvider */}
  </StrictMode>
);

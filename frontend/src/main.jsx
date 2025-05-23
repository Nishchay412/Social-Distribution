import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.jsx';
import Signup from './authentication/Signup';
import { Dashboard } from './dashboard/dashboard';
import { Admin_Dashboard } from './Node_Management/AdminDashboard.jsx';
import Login from './authentication/Login';
import { User_Profile } from './dashboard/user_profile';
import { Follower_List } from './Following/FollowersList.jsx';
import { Followee_List } from './Following/FolloweesList.jsx';
import { Friend_Profile } from './dashboard/friend_user_profile';
import { Follow_Requests } from './dashboard/follow_requests.jsx';
import AuthorList from './posting/AuthorList';
import EditPost from './posting/EditPost';
import UserPosts from './posting/UserPosts';
import MyPosts from './posting/Personalposts';
import CreatePost from './posting/CreatePost';
import PublicPosts from './posting/publicposts';
import { Header } from './dashboard/leftpanel';
import { CreatePost1 } from './posting/CreatePost1';
import PostDetails from './posting/singlepost';
import FriendsPosts from './posting/FriendsPost';
import User_Management from './Node_Management/UserManagement';
import AdminSignup from './Node_Management/AdminSignup';
import Admin_Edit_User from './Node_Management/AdminEditUser';
import AdminPendingUsers from './Node_Management/AdminPendingUsers';
import AdminRegisterUser from './Node_Management/AdminRegisterUser';
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
    path: "/user-management",
    element: <User_Management />,
  },
  {
    path: "/admin-dashboard",
    element: <Admin_Dashboard />,
  },
  {
    path: "/admin-edit-user",
    element: <Admin_Edit_User />,
  },
  {
    path: "/sign-up",
    element: <Signup />,
  },
  {
    path: "/admin-sign-up",
    element: <AdminSignup/>,
  },
  {
    path: "/admin-pending-users",
    element: <AdminPendingUsers/>,
  },
  {
    path: "/login",
    element: <Login />,
  },
  {
    path: "/admin-register-user",
    element: <AdminRegisterUser />,
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
    path:"/profile/:username/followers",
    element:<Follower_List/>,
  },
  {
    path:"/profile/:username/followees",
    element:<Followee_List/>,
  },
  {
    path: "/profile/:username",  // ✅ Dynamic Route for Friend's Profile
    element: <Friend_Profile />,
  },
  {
    path:"/follow-requests",
    element: <Follow_Requests/>,
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
    path: "/post/:id",  // ✅ Cleaner URL for user's posts
    element: <PostDetails />,
  },
  {
    path: "/friendspost",  // ✅ Cleaner URL for user's posts
    element: <FriendsPosts/>,
  },
  {
    path: "/publicposts",  // ✅ Cleaner URL for user's posts
    element: <PublicPosts />,
  },
  {
    path: "/Header",  // ✅ Cleaner URL for user's posts
    element: <Header/>,
  },
  {
    path: "/createpost1",  // ✅ Cleaner URL for user's posts
    element: <CreatePost1/>,
  },
  
]);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={router} />  {/* ✅ Correctly rendering RouterProvider */}
  </StrictMode>
);

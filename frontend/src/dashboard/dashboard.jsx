import React from "react";
import { useNavigate } from "react-router-dom";
import CreatePost from "../posting/CreatePost";
import { Header } from "./leftpanel";
import { TopPanel } from "./toppanel";
import PublicPosts from "../posting/publicposts";
export function Dashboard() {
    const navigate = useNavigate();

    const navigateToProfile = () => navigate("/profile");
    const profile_pic =localStorage.getItem("profilepic")
    console.log(profile_pic)
    const navigateToMyPosts = () => navigate("/my-posts");

    const handleLogout = async () => {
        try {
            const response = await fetch("http://127.0.0.1:8000/logout/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
                },
                body: JSON.stringify({ refresh: localStorage.getItem("refresh_token") }),
            });

            if (!response.ok) {
                throw new Error("Failed to logout. Please try again.");
            }

            ["access_token", "refresh_token", "email", "firstname", "lastname", "username"].forEach(item => localStorage.removeItem(item));
            navigate("/login");
        } catch (error) {
            console.error("Logout error:", error);
            alert("Logout failed. Please check your connection and try again.");
        }
    };

    return (
        <div className=" min-h-screen">
          {/* Top Panel (Navigation, Search, Profile) */}
          <TopPanel />
    
          {/* Main Layout */}
          <div className="flex mt-4">
            {/* Sidebar (Navigation, Contacts) */}
            <div className="w-1/4 border-r border-gray-300 px-4">
              <Header />
            </div>
    
            {/* Main Content (Feed) */}
            <div className="flex flex-col w-3/4 mx-auto max-w-3xl">
              {/* Create Post at the Top */}
              <div className="mb-6">
                <CreatePost />
              </div>

            <div className="mb-6 text-center">
            <button
              onClick={navigateToMyPosts}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              View My Posts
            </button>
          </div>
    
              {/* Placeholder for Feed Posts */}
              <div className="bg-white rounded-lg shadow-md p-4">
                <h2 className="text-lg font-semibold">Recent Posts</h2>
                <p className="text-gray-500">Posts will appear here...</p>
                <PublicPosts/>
                
              </div>
            </div>
          </div>
        </div>
      );
    }
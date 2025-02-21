import React from "react";
import { useNavigate } from "react-router-dom";
import CreatePost from "../posting/CreatePost";
import { Header } from "./leftpanel";

export function Dashboard() {
    const navigate = useNavigate();

    const navigateToProfile = () => navigate("/profile");
    const profile_pic =localStorage.getItem("profilepic")
    console.log(profile_pic)

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
          <div className="flex h-screen justify-between">
            {/* Sidebar Header (1/3 width) */}
            <div className="w-1/4 border-r border-gray-300 p-4">
              <Header />
            </div>
      
            {/* Main Content (2/3 width) */}
            <div className="flex flex-col  justify-center w-2/4 p-6">
              <h1 className="text-2xl font-bold mb-6">Welcome to the Dashboard!</h1>
      
              {/* Buttons */}
              
              
      
              {/* Create Post Component */}
              <CreatePost />
            </div>
            <div className="">
                <img src= {profile_pic} className="w-12 h-12 rounded-4xl">
                </img>
            </div>
          </div>
        );
      }
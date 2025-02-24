import React from "react";
import { useNavigate } from "react-router-dom";
import CreatePost from "../posting/CreatePost";
import { Header } from "./leftpanel";
import { TopPanel } from "./toppanel";
import PublicPosts from "../posting/publicposts";
import { useState } from "react";

import MyPosts from "../posting/Personalposts";
import FriendsPosts from "../posting/FriendsPost";

export function Dashboard() {
  const navigate = useNavigate();
  const [selectedFeed, setSelectedFeed] = useState("public"); // Default feed

  // Navigation functions
  const navigateToProfile = () => navigate("/profile");
  const navigateToMyPosts = () => navigate("/my-posts");

  // Logout handler
  const handleLogout = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/logout/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({
          refresh: localStorage.getItem("refresh_token"),
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to logout. Please try again.");
      }

      ["access_token", "refresh_token", "email", "firstname", "lastname", "username"].forEach(
        (item) => localStorage.removeItem(item)
      );
      navigate("/login");
    } catch (error) {
      console.error("Logout error:", error);
      alert("Logout failed. Please check your connection and try again.");
    }
  };

  // Render the appropriate feed based on the selected option
  const renderFeedComponent = () => {
    switch (selectedFeed) {
      case "public":
        return <PublicPosts />;
      
      case "my":
        return <MyPosts />;
      case "friends":
        return <FriendsPosts />;
      default:
        return <PublicPosts />;
    }
  };

  return (
    <div className="min-h-screen">
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

          {/* Feed Selection Dropdown */}
          <div className="mb-6 text-center">
            <select
              value={selectedFeed}
              onChange={(e) => setSelectedFeed(e.target.value)}
              className="p-2 border border-gray-300 rounded"
            >
              <option value="public">Public Posts</option>
             
              <option value="my">My Posts</option>
              <option value="friends">Friends' Posts</option>
            </select>
          </div>

          {/* Feed Display Area */}
          <div className="bg-white rounded-lg shadow-md p-4">
            {renderFeedComponent()}
          </div>
        </div>
      </div>
    </div>
  );
}

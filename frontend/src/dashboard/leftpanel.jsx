import React from "react";
import { Navigate, useNavigate } from "react-router-dom";

export function Header() {
    const navigate = useNavigate();

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

            // Clear tokens from localStorage
            ["access_token", "refresh_token", "email", "firstname", "lastname", "username"].forEach(item => localStorage.removeItem(item));

            // Redirect to login page
            navigate("/login");
        } catch (error) {
            console.error("Logout error:", error);
            alert("Logout failed. Please check your connection and try again.");
        }
    };
    const handleUserProfile = async()=> await navigate("/profile")

    // Define header elements *after* handleLogout is available
    const headerelements = [
        { id: 1, name: "feed", img: "/homeicon.png", action: null },
        { id: 2, name: "settings", img: "/settings.png", action: null},
        { id: 3, name: "Log Out", img: "/logout.png", action: handleLogout },
        { id: 4, name: "Profile", img: "/userprofile.png", action: handleUserProfile },

    ];

    return (
      <div className="w-full border-b border-gray-300">
        <div className="flex flex-col gap-2 w-full cursor-pointer">
          {headerelements.map((item) => (
            <div 
              key={item.id} 
              className="flex items-center gap-2 w-full hover:bg-gray-200 p-2 rounded" 
              onClick={item.action}
            >
              <span>{item.name}</span>
              <img src={item.img} alt={item.name} className="w-6 h-6" />
            </div>
          ))}
        </div>
  
        {/* Friends Section */}
        <div className="mt-4 font-bold">My Friends</div>
      </div>
    );
}

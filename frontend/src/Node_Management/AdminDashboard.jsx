import React from "react";
import { useNavigate } from "react-router-dom";
import User_Management from "./UserManagement";

export function Admin_Dashboard() {
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

    return (
        <div className=" min-h-screen">
            <button 
            id="logout-btn"
            className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600" 
            onClick={() => handleLogout()}>
                Log Out
            </button>

            <h1>Admin Dashboard</h1>
            <User_Management/>
        </div>
      );

}
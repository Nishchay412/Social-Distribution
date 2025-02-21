import React from "react";
import { useNavigate } from "react-router-dom";
import CreatePost from "../posting/CreatePost";

export function Dashboard() {
    const navigate = useNavigate();

    const navigateToProfile = () => navigate("/profile");

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
        <div className="flex flex-col items-center justify-center h-screen bg-gray-100 p-4">
            <h1 className="text-2xl font-bold mb-6">Welcome to the Dashboard!</h1>
            <div className="flex gap-4 mb-6">
                <button 
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
                    onClick={navigateToProfile}
                >
                    User Profile
                </button>
                <button 
                    className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition"
                    onClick={handleLogout}
                >
                    Logout
                </button>
            </div>
            <CreatePost />
        </div>
    );
}
import React from "react";
import { useNavigate } from "react-router-dom";

export function Dashboard() {
    const navigate = useNavigate();  // ✅ Hook to navigate

    const navigate_profile = () => {
        navigate("/profile");  // ✅ Call navigate to go to /login
    };
    // ✅ Function to handle logout
    const handleLogout = async () => {
        try {
            const response = await fetch("http://127.0.0.1:8000/logout/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${localStorage.getItem("access_token")}`
                },
                body: JSON.stringify({
                    refresh: localStorage.getItem("refresh_token")
                })
            });

            if (response.ok) {
                // ✅ Clear tokens from localStorage
                localStorage.removeItem("access_token");
                localStorage.removeItem("refresh_token");
                localStorage.removeItem("email");
                localStorage.removeItem("firstname");
                localStorage.removeItem("lastname");
                localStorage.removeItem("username");

                // ✅ Redirect to login
                navigate("/login");
            } else {
                console.error("Failed to logout. Please try again.");
            }
        } catch (error) {
            console.error("Network error:", error);
        }
    };

    return (
        <div>
            <h1>Welcome to the Dashboard!</h1>
            <div className="flex gap-3 ">
            <button 
                className="bg-red-500 text-white p-2 rounded hover:bg-red-600 mt-4"
                onClick={handleLogout}   // ✅ Call handleLogout on click
            >
                Logout
            </button>
            <button 
                className="bg-red-500 text-white p-2 rounded hover:bg-red-600 mt-4"
                onClick={navigate_profile}   // ✅ Call handleLogout on click
            >
                User Profile
            </button>
            

            </div>
            
        </div>
    );
}

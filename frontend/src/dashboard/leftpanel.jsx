import React from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
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

    const [users, setUsers] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchUsers = async () => {
      const accessToken = localStorage.getItem("access_token"); // Get token from localStorage

      if (!accessToken) {
        setError("No access token found. Please log in.");
        return;
      }

      try {
        const response = await fetch("http://127.0.0.1:8000/users/exclude-self/", {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${accessToken}`,
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        setUsers(data); // Store fetched users in state

      } catch (error) {
        console.error("Error fetching users:", error);
        setError("Failed to fetch users. Please try again.");
      }
    };

    fetchUsers();
  }, []); // Runs once when the component mounts

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
        <div className="mt-4 font-bold">People you may know</div>
        {error ? (
        <p className="text-red-500">{error}</p>
      ) : users.length === 0 ? (
        <p className="text-gray-500">No users found.</p>
      ) : (
        <ul className="space-y-3">
          {users.map((user) => (
            <li key={user.id} className="p-2 bg-gray-100 rounded-lg">
              <strong>{user.username}</strong> - {user.email}
            </li>
          ))}
        </ul>
      )}
      </div>
    );
}

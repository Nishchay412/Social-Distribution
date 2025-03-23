import React, { useEffect, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import Admin_Edit_User from "./AdminEditUser";
import { API_BASE_URL } from "../../config";



const User_Management = () => {
    const navigate = useNavigate();
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [editing, setEditing] = useState(false);

    const accessToken = localStorage.getItem("access_token");

    if (!accessToken) {
        setError("You must be an admin to access this.");
        return;
    }

    // Navigating to other sections
    const userprofile = async (username) => {
        if (!username) {
          console.error("Username is undefined!");
          return;
        }
        console.log("Navigating to profile:", username);
        navigate(`/profile/${username}`);
      };

    // Handle deleting users
    const handleDelete = async (username) => {
        try {
          const res = await fetch(
            `${API_BASE_URL}/users/exclude-self/${username}/delete-user/`,
            {
              method: "DELETE",
              headers: {
                Authorization: `Bearer ${accessToken}`,
                "Content-Type": "application/json",
              },
            }
          );
      
          if (!res.ok) {
            const errorText = await res.text();
            throw new Error(`Delete failed: ${res.status} ${errorText}`);
          }
      
          // Optionally, you could remove the deleted user from state instead of reloading the page:
          window.location.reload();
        } catch (error) {
          console.error(`Error deleting user ${username}:`, error);
          setError(`Error deleting user ${username}.`);
        }
      };
      

    useEffect(() => {
        const fetchUsers = async () => {
            setLoading(true);

            try {
                const response = await fetch("${API_BASE_URL}/users/exclude-self/", {
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
            } finally {
                setLoading(false);
            }
        };

        fetchUsers();
    }, []);

    if (loading) return <p className="text-center text-lg">Loading users...</p>;
    if (error) return <p className="text-center text-red-500">{error}</p>;

    return (
        <div className="flex flex-col items-center w-full bg-gray-100 p-6">
          <div className="max-w-3xl w-full">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Verdigras Users</h2>
                {error ? (
                <p className="text-red-500">{error}</p>
            ) : users.length === 0 ? (
                <p className="text-gray-500">No users found.</p>
             ) : (
                <ul className="space-y-3">
                    {users.map((user) => (
                        <li 
                        key={user.username} 
                        className="p-2 bg-gray-100 rounded-lg cursor-pointer hover:bg-gray-200 transition"
                        >
                        <strong>{user.username}</strong> - {user.email} 

                        <div className="flex justify-between items-center mt-4 text-gray-500 text-sm">
                            <div className="flex gap-4">
                                <button
                                className="flex items-center gap-1 hover:text-blue-500 transition"
                                onClick={() => setEditing(true)}
                                >
                                📝 Edit
                                </button>
                                {editing && <Admin_Edit_User user={user} onClose={() => setEditing(false)}/>}
                                <button 
                                    onClick={() => handleDelete(user.username)}
                                    className="flex items-center gap-1 hover:text-red-500 transition">
                                🗑️ Delete
                                </button>
                            </div>
                        </div>
                    </li>
                
                ))}
            </ul>
             )}
          </div>
        </div>
      );
};

export default User_Management;
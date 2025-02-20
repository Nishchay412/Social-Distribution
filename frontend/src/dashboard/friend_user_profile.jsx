import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

export function Friend_Profile() {
    const { username } = useParams();  // ✅ Get username from URL
    const [userData, setUserData] = useState(null);
    const [error, setError] = useState(null);

    // ✅ Fetch user data by username
    useEffect(() => {
        const fetchUserProfile = async () => {
            try {
                const response = await fetch(`http://127.0.0.1:8000/profile/${username}/`);
                const data = await response.json();

                if (response.ok) {
                    setUserData(data);
                } else {
                    setError(data.error || "User not found.");
                }
            } catch (error) {
                setError("Something went wrong. Please try again.");
            }
        };

        fetchUserProfile();
    }, [username]);  // ✅ Refetch when the username in the URL changes

    if (error) {
        return (
            <div className="flex justify-center items-center min-h-screen">
                <div className="border-2 p-12 rounded shadow-lg flex flex-col items-center w-96">
                    <h2 className="text-2xl font-bold text-red-500 mb-4">Error</h2>
                    <p>{error}</p>
                </div>
            </div>
        );
    }

    if (!userData) {
        return (
            <div className="flex justify-center items-center min-h-screen">
                <div className="border-2 p-12 rounded shadow-lg flex flex-col items-center w-96">
                    <h2 className="text-2xl font-bold text-gray-500 mb-4">Loading...</h2>
                </div>
            </div>
        );
    }

    return (
        <div className="flex justify-center items-center min-h-screen">
            <div className="border-2 p-12 rounded shadow-lg flex flex-col items-center w-96">
                {/* ✅ Profile Image */}
                <img
                    src={userData.profile_picture || "https://via.placeholder.com/150?text=User"}
                    alt="Profile"
                    className="w-24 h-24 rounded-full border-2 border-gray-300 mb-4"
                />

                <h2 className="text-2xl font-bold mb-4">{userData.username}'s Profile</h2>

                <div className="text-left w-full space-y-2">
                    <p><strong>Username:</strong> {userData.username}</p>
                    <p><strong>First Name:</strong> {userData.first_name}</p>
                    <p><strong>Last Name:</strong> {userData.last_name}</p>
                    <p><strong>Email:</strong> {userData.email}</p>
                </div>
            </div>
        </div>
    );
}

import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

export function Friend_Profile() {
    const { username } = useParams(); // Get username from URL (e.g. /profile/:username)

    // State for user profile
    const [userData, setUserData] = useState(null);

    // State for user posts
    const [posts, setPosts] = useState([]);

    // State for errors
    const [error, setError] = useState(null);

    // Fetch user profile
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
            } catch (err) {
                setError("Something went wrong fetching the user profile.");
            }
        };

        fetchUserProfile();
    }, [username]);

    // Fetch user posts (requires authentication via Bearer token)
    useEffect(() => {
        const fetchUserPosts = async () => {
            try {
                // Retrieve token from localStorage
                const token = localStorage.getItem("access_token");

                // Make a GET request to the endpoint that returns the user's posts
                // Adjust the URL to match your actual route
                const response = await fetch(
                    `http://127.0.0.1:8000/api/users/${username}/posts/`,
                    {
                        headers: {
                            // Include the Bearer token for authentication
                            Authorization: `Bearer ${token}`,
                        },
                    }
                );

                const data = await response.json();

                if (response.ok) {
                    setPosts(data);
                } else {
                    setError(data.error || "Failed to fetch user posts.");
                }
            } catch (err) {
                setError("Something went wrong fetching user posts.");
            }
        };

        fetchUserPosts();
    }, [username]);

    // Show an error message if any errors occurred
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

    // While user data is still loading
    if (!userData) {
        return (
            <div className="flex justify-center items-center min-h-screen">
                <div className="border-2 p-12 rounded shadow-lg flex flex-col items-center w-96">
                    <h2 className="text-2xl font-bold text-gray-500 mb-4">Loading...</h2>
                </div>
            </div>
        );
    }

    // Once everything is loaded, render the profile and the user’s posts
    return (
        <div className="flex justify-center items-center min-h-screen">
            <div className="border-2 p-12 rounded shadow-lg flex flex-col items-center w-96">
                {/* Profile Image */}
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

                {/* Display the user's posts */}
                <div className="text-left w-full space-y-2 mt-6">
                    <h3 className="text-xl font-bold mb-2">Posts by {userData.username}:</h3>
                    {posts.length === 0 ? (
                        <p>No posts to display.</p>
                    ) : (
                        posts.map((post) => (
                            <div key={post.id} className="border-b border-gray-300 py-2">
                                {/* Adjust these fields to match your Post data structure */}
                                <h4 className="font-semibold">{post.title}</h4>
                                <p className="text-gray-700">{post.content}</p>
                                <p className="text-xs text-gray-400">
                                    Published: {new Date(post.published).toLocaleString()}
                                </p>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}

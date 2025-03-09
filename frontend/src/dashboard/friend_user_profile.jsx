import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import Profile_Button from "../Following/ProfileButton";

export function Friend_Profile() {
  const { username } = useParams(); // e.g., /profile/:username

  const [userData, setUserData] = useState(null);
  const [posts, setPosts] = useState([]);
  const [error, setError] = useState(null);
  const [friendStatus, setFriendStatus] = useState(""); // To display result of adding friend
  const [loading, setLoading] = useState(true);

  // Retrieve the token from localStorage for authenticated requests
  const token = localStorage.getItem("access_token");

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
      } finally {
        setLoading(false);
      }
    };

    fetchUserProfile();
  }, [username]);

  // Fetch user posts
  useEffect(() => {
    const fetchUserPosts = async () => {
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/api/users/${username}/posts/`,
          {
            headers: {
              Authorization: `Bearer ${token}`, // Include the Bearer token
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

    if (token) {
      fetchUserPosts();
    } else {
      setError("You need to be logged in to view posts.");
    }
  }, [username, token]);

  // Handle adding friend
  const handleAddFriend = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/friends/add/${username}/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.error || "Failed to add friend");
      }

      setFriendStatus("Friend added successfully!");
    } catch (err) {
      console.error("Error adding friend:", err);
      setFriendStatus(err.message);
    }
  };

  // Show loading state while profile data is being fetched
  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <p>Loading...</p>
      </div>
    );
  }

  // If there's an error, display it
  if (error) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <p className="text-red-500">{error}</p>
      </div>
    );
  }

  // Render the profile and the user's posts (userData is guaranteed to exist here)
  return (
    <div className="flex justify-center items-center min-h-screen">
      <div className="border-2 p-12 rounded shadow-lg flex flex-col items-center w-96">
        {/* Follow Button from Following dir */}
        <Profile_Button/>
        {/* Profile Image */}
        <img
          src={
            userData.profile_picture ||
            "https://via.placeholder.com/150?text=User"
          }
          alt="Profile"
          className="w-24 h-24 rounded-full border-2 border-gray-300 mb-4"
        />

        <h2 className="text-2xl font-bold mb-4">{userData.username}'s Profile</h2>

        <div className="text-left w-full space-y-2">
          <p>
            <strong>Username:</strong> {userData.username}
          </p>
          <p>
            <strong>First Name:</strong> {userData.first_name}
          </p>
          <p>
            <strong>Last Name:</strong> {userData.last_name}
          </p>
          <p>
            <strong>Email:</strong> {userData.email}
          </p>
        </div>

        {/* Add Friend Button */}
        <button
          onClick={handleAddFriend}
          className="mt-4 bg-purple-500 hover:bg-purple-600 text-white py-2 px-4 rounded"
        >
          Add Friend
        </button>

        {/* Friend Status Message */}
        {friendStatus && <p className="mt-2 text-sm">{friendStatus}</p>}

        {/* Display the user's posts */}
        <div className="text-left w-full space-y-2 mt-6">
          <h3 className="text-xl font-bold mb-2">Posts by {userData.username}:</h3>
          {posts.length === 0 ? (
            <p>No posts to display.</p>
          ) : (
            posts.map((post) => (
              <div key={post.id} className="border-b border-gray-300 py-2">
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

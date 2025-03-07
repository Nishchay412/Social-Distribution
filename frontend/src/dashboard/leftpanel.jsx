import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export function Header() {
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/logout/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
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

  const handleUserProfile = async () => await navigate("/profile");
  const handleNotifs = async () => await navigate("/follow-requests");

  const headerelements = [
    { id: 1, name: "Home", img: "/homeicon.png", action: null },
    { id: 2, name: "Profile", img: "/userprofile.png", action: handleUserProfile},
    { id: 3, name: "Notifs", action: handleNotifs},
    { id: 4, name: "Settings", img: "/settings.png", action: null },
    { id: 5, name: "Log Out", img: "/logout.png", action: handleLogout },
    
  ];

  const [users, setUsers] = useState([]);
  const [friends, setFriends] = useState([]); // Stores list of friends
  const [error, setError] = useState(null);
  const [friendsError, setFriendsError] = useState(null);

  const userProfile = async (username) => {
    if (!username) {
      console.error("Username is undefined!");
      return;
    }
    console.log("Navigating to profile:", username);
    navigate(`/profile/${username}`);
  };

  // Fetch people you may know
  useEffect(() => {
    const fetchUsers = async () => {
      const accessToken = localStorage.getItem("access_token");

      if (!accessToken) {
        setError("No access token found. Please log in.");
        return;
      }

      try {
        const response = await fetch("http://127.0.0.1:8000/users/non-friends", {
          method: "GET",
          headers: {
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        setUsers(data);
      } catch (error) {
        console.error("Error fetching users:", error);
        setError("Failed to fetch users. Please try again.");
      }
    };

    fetchUsers();
  }, []);

  // Fetch friends list
  useEffect(() => {
    const fetchFriends = async () => {
      const accessToken = localStorage.getItem("access_token");

      if (!accessToken) {
        setFriendsError("No access token found. Please log in.");
        return;
      }

      try {
        const response = await fetch("http://127.0.0.1:8000/friends/", {
          method: "GET",
          headers: {
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        setFriends(data);
      } catch (error) {
        console.error("Error fetching friends:", error);
        setFriendsError("Failed to fetch friends. Please try again.");
      }
    };

    fetchFriends();
  }, []);

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

      {/* People You May Know Section */}
      <div className="mt-4 font-bold">People you may know</div>
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
              onClick={() => userProfile(user.username)}
            >
              <strong>{user.username}</strong> - {user.email}
            </li>
          ))}
        </ul>
      )}

      {/* Friends List Section */}
      <div className="mt-6 font-bold">Your Friends</div>
      {friendsError ? (
        <p className="text-red-500">{friendsError}</p>
      ) : friends.length === 0 ? (
        <p className="text-gray-500">You have no friends yet.</p>
      ) : (
        <ul className="space-y-3">
          {friends.map((friend) => (
            <li
              key={friend.username}
              className="p-2 bg-blue-100 rounded-lg cursor-pointer hover:bg-blue-200 transition"
              onClick={() => userProfile(friend.username)}
            >
              <strong>{friend.username}</strong> - {friend.email}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

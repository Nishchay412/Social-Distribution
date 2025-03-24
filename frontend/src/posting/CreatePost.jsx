import React, { useState } from "react";
import axios from "axios";

import { API_BASE_URL } from '../../config';

export function CreatePost() {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  // Use a dropdown state for visibility. Default is "PUBLIC".
  const [visibility, setVisibility] = useState("PUBLIC");
  const [error, setError] = useState(null);
  const [message, setMessage] = useState("");

  const API_BASE_URL = `${API_BASE_URL}/posts/create/`;

  // Retrieve user's profile picture and first name from local storage
  const profilePic = localStorage.getItem("profilepic") || "/default-avatar.png";
  const firstName = localStorage.getItem("firstname") || "User";

  const getAuthToken = () => localStorage.getItem("access_token");

  const createPost = async (postData) => {
    try {
      const token = getAuthToken();
      if (!token) throw new Error("No authentication token found. Please log in.");

      const response = await axios.post(API_BASE_URL, postData, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data",
        },
      });

      return response.data;
    } catch (error) {
      console.error(
        "Error creating post:",
        error.response ? error.response.data : error.message
      );
      throw error;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      formData.append("title", title);
      formData.append("content", content);
      // Append the selected visibility option (e.g., PUBLIC, UNLISTED, FRIENDS, PRIVATE, DRAFT)
      formData.append("visibility", visibility);
      if (selectedFile) formData.append("image", selectedFile);

      const newPost = await createPost(formData);
      setMessage(`Post created successfully! ID: ${newPost.id}`);
      setTitle("");
      setContent("");
      setSelectedFile(null);
      setVisibility("PUBLIC"); // Reset visibility to default
      setError(null);
    } catch (err) {
      setError("Failed to create post.");
      setMessage("");
    }
  };

  return (
    <div className="flex flex-col items-center w-full bg-gray-100 p-4">
      <div className="bg-white p-5 rounded-2xl shadow-lg max-w-lg w-full">
        {/* Profile Picture & Input Fields */}
        <div className="flex items-center gap-3">
          <img src={profilePic} alt="User" className="w-12 h-12 rounded-full" />
          <div className="w-full flex flex-col gap-2">
            {/* Title Field */}
            <input
              type="text"
              placeholder="Title (optional)"
              className="w-full p-3 bg-gray-100 rounded-full outline-none"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
            {/* Content Field */}
            <input
              type="text"
              placeholder={`What's happening, ${firstName}? (optional)`}
              className="w-full p-3 bg-gray-100 rounded-full outline-none"
              value={content}
              onChange={(e) => setContent(e.target.value)}
            />
          </div>
        </div>

        {/* Upload Button & Visibility Dropdown */}
        <div className="flex justify-between items-center mt-4">
          {/* Image Upload Button */}
          <label className="cursor-pointer bg-gray-200 px-4 py-2 rounded-lg hover:bg-gray-300 transition">
            📸
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setSelectedFile(e.target.files[0])}
              className="hidden"
            />
          </label>

          {/* Visibility Dropdown */}
          <div className="flex items-center gap-2">
            <select
              value={visibility}
              onChange={(e) => setVisibility(e.target.value)}
              className="p-2 border border-gray-300 rounded-lg outline-none"
            >
              <option value="PUBLIC">Public</option>
              <option value="UNLISTED">Unlisted</option>
              <option value="FRIENDS">Friends Only</option>
              <option value="PRIVATE">Private</option>
              <option value="DRAFT">Draft</option>
            </select>
          </div>

          {/* Post Button */}
          <button
            onClick={handleSubmit}
            className="bg-pink-500 text-white px-4 py-2 rounded-full hover:bg-pink-600 transition"
            disabled={!title.trim() && !content.trim() && !selectedFile}
          >
            Post
          </button>
        </div>

        {/* Error & Success Messages */}
        {error && (
          <p className="text-red-600 bg-red-100 p-2 rounded-md text-sm mt-3">
            {error}
          </p>
        )}
        {message && (
          <p className="text-green-600 bg-green-100 p-2 rounded-md text-sm mt-3">
            {message}
          </p>
        )}
      </div>
    </div>
  );
}

export default CreatePost;

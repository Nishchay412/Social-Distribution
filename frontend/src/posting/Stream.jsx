import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from "react-markdown";

// Helper function to build the full image URL from a relative path.
function getImageUrl(path) {
  if (!path) return "";
  // If already a full URL, return it.
  if (path.startsWith("http")) return path;
  // If the path already includes "/media" (or "media"), remove any extra leading slash.
  if (path.startsWith("/media") || path.startsWith("media")) {
    const normalized = path.replace(/^\/+/, ""); // remove leading slash(es)
    return `http://127.0.0.1:8000/${normalized}`;
  }
  // Otherwise, assume it's something like "images/foo.png" and prepend "/media/"
  return `http://127.0.0.1:8000/media/${path}`;
}

const Stream = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  
  // Get the JWT token from localStorage
  const token = localStorage.getItem("access_token");

  useEffect(() => {
    const fetchStreamPosts = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/api/stream/", {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        setPosts(response.data);
      } catch (err) {
        console.error("Error fetching stream posts:", err.response?.data || err.message);
        setError("Failed to fetch stream posts.");
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchStreamPosts();
    } else {
      setError("Not authenticated.");
      setLoading(false);
    }
  }, [token]);

  if (loading) return <p className="text-center">Loading posts...</p>;
  if (error) return <p className="text-center text-red-500">{error}</p>;

  return (
    <div className="max-w-3xl mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4">Your Stream</h2>
      {posts.length === 0 ? (
        <p>No posts to display.</p>
      ) : (
        <ul className="space-y-6">
          {posts.map((post) => (
            <li key={post.id} className="bg-white p-5 rounded-lg shadow-md">
              <h3 className="text-xl font-bold">{post.title}</h3>
              <div className="text-gray-700 markdown-content">
                <ReactMarkdown>{post.content}</ReactMarkdown>
              </div>
              {post.image && (
                <img
                  src={getImageUrl(post.image)}
                  alt="Post"
                  className="mt-3 w-full h-auto rounded"
                />
              )}
              <div className="text-xs text-gray-500 mt-2">
                Published: {new Date(post.published).toLocaleString()}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Stream;

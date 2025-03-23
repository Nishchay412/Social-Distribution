import React, { useState, useEffect } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import { API_BASE_URL } from '../../config';
// Helper function to build the correct image URL
function getImageUrl(path) {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  if (path.startsWith("/media") || path.startsWith("media")) {
    const normalized = path.replace(/^\/+/, ""); // remove leading slash
    return `${API_BASE_URL}/${normalized}`;
  }
  // Fallback: assume the image is stored in the media folder
  return `${API_BASE_URL}/media/${path}`;
}

function DraftPosts() {
  const [posts, setPosts] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const token = localStorage.getItem("access_token");

  useEffect(() => {
    const fetchDraftPosts = async () => {
      try {
        const response = await axios.get("${API_BASE_URL}/posts/drafts/", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setPosts(response.data);
      } catch (err) {
        console.error("Error fetching draft posts:", err.response?.data || err.message);
        setError("Failed to fetch draft posts.");
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchDraftPosts();
    } else {
      setError("Not authenticated.");
      setLoading(false);
    }
  }, [token]);

  if (loading) return <p>Loading draft posts...</p>;
  if (error) return <p className="text-red-500">{error}</p>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Draft Posts</h2>
      {posts.length === 0 ? (
        <p>No draft posts available.</p>
      ) : (
        <ul className="space-y-6">
          {posts.map((post) => (
            <li key={post.id} className="bg-white p-4 rounded shadow">
              <h3 className="text-xl font-semibold">{post.title}</h3>
              <div className="text-gray-700 markdown-content">
                <ReactMarkdown>{post.content}</ReactMarkdown>
              </div>
              {post.image && (
                <img
                  src={getImageUrl(post.image)}
                  alt="Draft Post"
                  className="mt-2 w-full h-auto rounded"
                />
              )}
              <small className="text-gray-500">
                Created: {new Date(post.published).toLocaleString()}
              </small>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default DraftPosts;

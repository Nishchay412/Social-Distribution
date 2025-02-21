import React, { useEffect, useState } from "react";
import axios from "axios";

const PublicPosts = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const API_URL = "http://127.0.0.1:8000/api/posts/public/";

  useEffect(() => {
    const fetchPublicPosts = async () => {
      setLoading(true);
      const token = localStorage.getItem("access_token"); // Get JWT token

      try {
        const response = await axios.get(API_URL, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        setPosts(response.data);
      } catch (err) {
        setError("Failed to fetch public posts.");
        console.error("Error fetching posts:", err.response?.data || err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPublicPosts();
  }, []);

  if (loading) return <p className="text-center text-lg">Loading public posts...</p>;
  if (error) return <p className="text-center text-red-500">{error}</p>;

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-6">
      <div className="bg-white p-6 rounded-lg shadow-md max-w-3xl w-full">
        <h2 className="text-3xl font-bold text-center text-gray-800 mb-6">Public Posts</h2>

        {posts.length === 0 ? (
          <p className="text-center text-gray-600">No public posts available.</p>
        ) : (
          <ul className="space-y-6">
            {posts.map((post) => (
              <li key={post.id} className="p-4 border rounded-lg bg-gray-50">
                <h3 className="text-xl font-semibold text-gray-800">{post.title}</h3>
                <p className="text-gray-700">{post.content}</p>
                {post.image && (
                  <img src={post.image} alt="Post" className="mt-3 w-full h-auto rounded-lg shadow-md" />
                )}
                <p className="text-sm text-gray-500 mt-2">
                  <strong>Author:</strong> {post.author_username} | <strong>Published:</strong>{" "}
                  {new Date(post.published).toLocaleString()}
                </p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default PublicPosts;

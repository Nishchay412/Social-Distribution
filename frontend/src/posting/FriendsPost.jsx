import React, { useEffect, useState } from "react";
import axios from "axios";

function FriendsPosts() {
  const [posts, setPosts] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const token = localStorage.getItem("access_token");

  useEffect(() => {
    const fetchFriendsPosts = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/friends/posts/", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setPosts(response.data);
      } catch (err) {
        console.error("Error fetching friends' posts:", err.response?.data || err.message);
        setError("Failed to fetch friends' posts.");
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchFriendsPosts();
    } else {
      setError("You need to be logged in to view friends' posts.");
      setLoading(false);
    }
  }, [token]);

  if (loading) return <p>Loading friends' posts...</p>;
  if (error) return <p className="text-red-500">{error}</p>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Friends' Posts</h2>
      {posts.length === 0 ? (
        <p>No posts from your friends yet.</p>
      ) : (
        <ul className="space-y-6">
          {posts.map((post) => (
            <li key={post.id} className="bg-white p-4 rounded shadow">
              {/* Title and Author */}
              <h3 className="text-xl font-semibold">{post.title}</h3>
              <p className="text-sm text-gray-600">
                <strong>Author:</strong> {post.author_username}
              </p>

              {/* Content */}
              <p className="text-gray-700 mt-2">{post.content}</p>

              {/* Image (if any) */}
              {post.image && (
                <img
                  src={post.image}
                  alt="Post"
                  className="mt-2 w-full h-auto rounded"
                />
              )}

              {/* Published Date */}
              <small className="text-gray-500 block mt-2">
                Published: {new Date(post.published).toLocaleString()}
              </small>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default FriendsPosts;

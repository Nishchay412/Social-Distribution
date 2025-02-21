import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const MyPosts = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate(); // Allows navigation

  useEffect(() => {
    const fetchMyPosts = async () => {
      setLoading(true);
      const token = localStorage.getItem("access_token"); // JWT token

      try {
        const response = await fetch("http://127.0.0.1:8000/posts/my/", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch your posts.");
        }

        const data = await response.json();
        setPosts(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchMyPosts();
  }, []);

  // Navigate to edit page
  const handleEdit = (postId, e) => {
    e.stopPropagation(); // Prevent triggering view-detail navigation
    navigate(`/posts/${postId}/edit`);
  };

  // Navigate to post detail page when clicking on the post item
  const handleView = (postId) => {
    navigate(`/posts/${postId}`);
  };

  if (loading) return <p>Loading your posts...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div>
      <h2>My Posts</h2>
      {posts.length === 0 ? (
        <p>You haven't posted anything yet.</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {posts.map((post) => (
            <li
              key={post.id}
              style={{
                display: "flex",
                alignItems: "center",
                marginBottom: "10px",
                border: "1px solid #ccc",
                padding: "10px",
                borderRadius: "8px",
                cursor: "pointer",
              }}
              onClick={() => handleView(post.id)}
            >
              <div style={{ flex: 1 }}>
                <h3>{post.title}</h3>
                <p>{post.content}</p>
                {post.image && <img src={post.image} alt="Post" width="200" />}
                <p>
                  <strong>Published:</strong>{" "}
                  {new Date(post.published).toLocaleString()}
                </p>
              </div>
              <button
                onClick={(e) => handleEdit(post.id, e)}
                style={{
                  marginLeft: "10px",
                  padding: "5px 10px",
                  cursor: "pointer",
                }}
              >
                ✏️ Edit
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default MyPosts;
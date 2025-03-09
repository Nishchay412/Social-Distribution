import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

// Helper function to build the full image URL
function getImageUrl(path) {
  if (!path) return "";
  if (path.startsWith("http")) {
    return path;
  }
  if (path.startsWith("/media") || path.startsWith("media")) {
    const normalized = path.replace(/^\/+/, ""); // remove leading slash
    return `http://127.0.0.1:8000/${normalized}`;
  }
  // Fallback: assume we need "/media/" in front
  return `http://127.0.0.1:8000/media/${path}`;
}


const MyPosts = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // For storing comment input per post
  const [commentTextByPostId, setCommentTextByPostId] = useState({});
  // For storing newly added comments so they appear immediately
  const [commentsByPostId, setCommentsByPostId] = useState({});

  // For inline editing
  const [editingPostId, setEditingPostId] = useState(null);
  const [editingData, setEditingData] = useState({ title: "", content: "" });

  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");

  // Fetch posts created by the logged-in user
  useEffect(() => {
    const fetchMyPosts = async () => {
      setLoading(true);
      try {
        const response = await axios.get("http://127.0.0.1:8000/posts/my/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setPosts(response.data);
      } catch (err) {
        setError("Failed to fetch your posts.");
        console.error(err.response?.data || err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchMyPosts();
  }, [token]);

    // Handle like toggle
  const handleLike = async (postId) => {
    try {
      await axios.post(
        `http://127.0.0.1:8000/posts/${postId}/likes/toggle/`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // Re-fetch posts to update like counts
      const response = await axios.get("http://127.0.0.1:8000/posts/my/", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setPosts(response.data);
    } catch (err) {
      console.error("Error liking post:", err.response?.data || err.message);
    }
  };

  const handleLikeComment = async (postId, commentId) => {
    try {
      await axios.post(
        `http://127.0.0.1:8000/posts/${postId}/comments/${commentId}/likes/toggle/`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // Re-fetch the “my” posts to get updated likes
      const response = await axios.get("http://127.0.0.1:8000/posts/my/", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setPosts(response.data);
    } catch (err) {
      console.error("Error liking comment:", err.response?.data || err.message);
    }
  };

  // Handle comment input changes
  const handleCommentChange = (postId, value) => {
    setCommentTextByPostId((prev) => ({
      ...prev,
      [postId]: value,
    }));
  };

  // Submit a new comment
  const handleCommentSubmit = async (postId) => {
    const commentText = commentTextByPostId[postId] || "";
    if (!commentText.trim()) return;

    try {
      const res = await axios.post(
        `http://127.0.0.1:8000/posts/${postId}/comments/create/`,
        { text: commentText },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // Clear the input
      setCommentTextByPostId((prev) => ({ ...prev, [postId]: "" }));
      // Add the new comment to local state
      const newComment = res.data;
      setCommentsByPostId((prev) => ({
        ...prev,
        [postId]: [...(prev[postId] || []), newComment],
      }));
    } catch (err) {
      console.error("Error creating comment:", err.response?.data || err.message);
    }
  };

  // Enter edit mode
  const handleEdit = (post) => {
    setEditingPostId(post.id);
    setEditingData({ title: post.title, content: post.content });
  };

  // Cancel edit mode
  const handleCancelEdit = () => {
    setEditingPostId(null);
    setEditingData({ title: "", content: "" });
  };

  // Save changes (PATCH request)
  const handleSaveEdit = async (postId) => {
    try {
      const response = await axios.patch(
        `http://127.0.0.1:8000/posts/${postId}/edit/`,
        editingData,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // Update local state
      setPosts((prevPosts) =>
        prevPosts.map((p) => (p.id === postId ? response.data : p))
      );
      // Exit edit mode
      setEditingPostId(null);
      setEditingData({ title: "", content: "" });
    } catch (err) {
      console.error("Error updating post:", err.response?.data || err.message);
      alert("Failed to update post");
    }
  };

  // Delete a post
  const handleDelete = async (postId) => {
    if (!window.confirm("Are you sure you want to delete this post?")) return;
    try {
      const response = await axios.delete(
        `http://127.0.0.1:8000/posts/${postId}/delete/`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (response.status === 200) {
        // Remove post from local state
        setPosts((prevPosts) => prevPosts.filter((p) => p.id !== postId));
      } else {
        throw new Error(response.data.error || "Failed to delete post");
      }
    } catch (err) {
      console.error("Error deleting post:", err.response?.data || err.message);
      alert(err.message || "Error deleting post");
    }
  };

  if (loading) return <p>Loading your posts...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div className="flex flex-col items-center bg-gray-100 p-6">
      <div className="max-w-3xl w-full bg-white rounded-lg shadow-md p-4">
        <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">
          My Posts
        </h2>
        {posts.length === 0 ? (
          <p className="text-center text-gray-500">
            You haven't posted anything yet.
          </p>
        ) : (
          <ul className="space-y-6">
            {posts.map((post) => (
              <li key={post.id} className="bg-white p-5 rounded-2xl shadow-md">
                {/* Post Header */}
                <div className="flex items-center gap-3 mb-3">
                  <img
                    src={post.author_profile_pic || "/default-avatar.png"}
                    alt="User"
                    className="w-10 h-10 rounded-full"
                  />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800">
                      {post.author_username || "You"}
                    </h3>
                    <p className="text-sm text-gray-500">
                      {new Date(post.published).toLocaleString()}
                    </p>
                  </div>
                </div>

                {/* Inline Edit vs. Normal View */}
                {editingPostId === post.id ? (
                  <div className="mb-4">
                    <input
                      type="text"
                      value={editingData.title}
                      onChange={(e) =>
                        setEditingData({ ...editingData, title: e.target.value })
                      }
                      className="w-full p-2 border border-gray-300 rounded mb-2"
                      placeholder="Edit title"
                    />
                    <textarea
                      value={editingData.content}
                      onChange={(e) =>
                        setEditingData({ ...editingData, content: e.target.value })
                      }
                      className="w-full p-2 border border-gray-300 rounded"
                      placeholder="Edit content"
                      rows="4"
                    />
                    <div className="mt-2 flex gap-3">
                      <button
                        onClick={() => handleSaveEdit(post.id)}
                        className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
                      >
                        Save
                      </button>
                      <button
                        onClick={handleCancelEdit}
                        className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      {post.title}
                    </h3>
                    <p className="text-gray-700">{post.content}</p>
                    {post.image && (
                      <img
                        src={getImageUrl(post.image)}
                        alt="Post"
                        className="mt-3 w-full h-auto rounded-lg shadow-md"
                      />
                    )}
                  </>
                )}

                 {/* Comments Section */}
                 <div className="mt-4 text-left">
                    <h4 className="text-sm font-semibold">Comments:</h4>
                    {post.comments?.length > 0 && (
                      <div>
                        {post.comments.map((comment) => (
                          <div key={comment.id} className="bg-gray-50 p-2 rounded-md mb-1 flex items-center justify-between">
                            <div>
                              <strong>{comment.author_username}:</strong> {comment.text}
                            </div>
                            
                            <div className="flex items-center gap-2">
                              <span className="text-sm text-gray-600">
                                {comment.likes_count || 0}
                            </span>
                            <button
                              onClick={() => handleLikeComment(post.id, comment.id)}
                              className="hover:text-pink-500 transition"
                            >
                              👍
                            </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                    {(commentsByPostId[post.id] || []).map((comment) => (
                      <div key={comment.id} className="bg-gray-50 p-2 rounded-md mb-1">
                        <strong>{comment.author_username}:</strong> {comment.text}
                      </div>
                    ))}
                  </div>

                {/* Social Actions */}
                <div className="flex justify-between items-center mt-4 text-gray-500 text-sm">
                  <div className="flex gap-4">
                    <button
                      onClick={() => handleLike(post.id)}
                      className="flex items-center gap-1 hover:text-pink-500 transition"
                    >
                      ❤️ Like
                    </button>
                    <button className="flex items-center gap-1 hover:text-blue-500 transition">
                      💬 Comment
                    </button>
                    <button className="flex items-center gap-1 hover:text-gray-800 transition">
                      🔄 Share
                    </button>
                  </div>
                  <span>{post.likes_count || 0} Likes</span>
                </div>

                {/* Comment Input */}
                <div className="flex items-center mt-4 gap-2">
                  <img
                    src="/userprofile.png"
                    alt="User"
                    className="w-8 h-8 rounded-full"
                  />
                  <input
                    type="text"
                    placeholder="Write a comment..."
                    className="w-full p-2 bg-gray-100 rounded-full outline-none"
                    value={commentTextByPostId[post.id] || ""}
                    onChange={(e) => handleCommentChange(post.id, e.target.value)}
                  />
                  <button
                    onClick={() => handleCommentSubmit(post.id)}
                    className="text-pink-500 hover:text-pink-600 transition"
                  >
                    ➤
                  </button>
                </div>

                {/* Edit and Delete Buttons */}
                {editingPostId !== post.id && (
                  <div className="mt-4 flex gap-4">
                    <button
                      onClick={() => handleEdit(post)}
                      className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                    >
                      ✏️ Edit
                    </button>
                    <button
                      onClick={() => handleDelete(post.id)}
                      className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
                    >
                      🗑️ Delete
                    </button>
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default MyPosts;
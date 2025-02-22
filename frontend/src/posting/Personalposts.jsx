import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const MyPosts = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  // For storing comment input per post
  const [commentTextByPostId, setCommentTextByPostId] = useState({});
  // For storing newly added comments (if you want to display them immediately)
  const [commentsByPostId, setCommentsByPostId] = useState({});

  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");

  // Fetch posts created by logged-in user
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

  // Handle like toggle for a post
  const handleLike = async (postId) => {
    try {
      await axios.post(
        `http://127.0.0.1:8000/posts/${postId}/likes/create/`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // Optionally, re-fetch posts to update like counts:
      const response = await axios.get("http://127.0.0.1:8000/posts/my/", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setPosts(response.data);
    } catch (err) {
      console.error("Error liking post:", err.response?.data || err.message);
    }
  };

  // Handle comment text changes for a given post
  const handleCommentChange = (postId, value) => {
    setCommentTextByPostId({
      ...commentTextByPostId,
      [postId]: value,
    });
  };

  // Handle comment submit for a given post
  const handleCommentSubmit = async (postId) => {
    const commentText = commentTextByPostId[postId] || "";
    if (!commentText.trim()) return;
    try {
      const res = await axios.post(
        `http://127.0.0.1:8000/posts/${postId}/comments/create/`,
        { text: commentText },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // Clear input
      setCommentTextByPostId({ ...commentTextByPostId, [postId]: "" });
      // Add the new comment to local state so it appears immediately
      const newComment = res.data; // expected to include id, author_username, text, etc.
      setCommentsByPostId((prev) => ({
        ...prev,
        [postId]: [...(prev[postId] || []), newComment],
      }));
    } catch (err) {
      console.error("Error creating comment:", err.response?.data || err.message);
    }
  };

  // Handle Edit button click – navigates to the edit page for that post
  const handleEdit = (postId) => {
    navigate(`/posts/${postId}/edit`);
  };

  if (loading) return <p>Loading your posts...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div className="flex flex-col items-center bg-gray-100 p-6">
      <div className="max-w-3xl w-full bg-white rounded-lg shadow-md p-4">
        <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">My Posts</h2>
        {posts.length === 0 ? (
          <p className="text-center text-gray-500">You haven't posted anything yet.</p>
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
                    <h3 className="text-lg font-semibold text-gray-800">{post.author_username || "You"}</h3>
                    <p className="text-sm text-gray-500">{new Date(post.published).toLocaleString()}</p>
                  </div>
                </div>

                {/* Post Content */}
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{post.title}</h3>
                <p className="text-gray-700">{post.content}</p>
                {post.image && (
                  <img
                    src={post.image}
                    alt="Post"
                    className="mt-3 w-full h-auto rounded-lg shadow-md"
                  />
                )}

                {/* Display any existing comments from backend */}
                <div className="mt-4 text-left">
                  <h4 className="text-sm font-semibold">Comments:</h4>
                  {post.comments && post.comments.length > 0 && (
                    <div>
                      {post.comments.map((comment) => (
                        <div key={comment.id} className="bg-gray-50 p-2 rounded-md mb-1">
                          <strong>{comment.author_username}:</strong> {comment.text}
                        </div>
                      ))}
                    </div>
                  )}
                  {/* Display locally added comments */}
                  {(commentsByPostId[post.id] || []).map((comment) => (
                    <div key={comment.id} className="bg-gray-50 p-2 rounded-md mb-1">
                        <p>
                        <strong>{comment.author_username}:</strong> {comment.text}
                      </p>
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

                {/* Edit Button */}
                <div className="mt-4">
                  <button
                    onClick={() => handleEdit(post.id)}
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                  >
                    ✏️ Edit
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default MyPosts;
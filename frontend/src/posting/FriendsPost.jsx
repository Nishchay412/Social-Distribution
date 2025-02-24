import React, { useEffect, useState } from "react";
import axios from "axios";

function FriendsPosts() {
  const [posts, setPosts] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [commentTextByPostId, setCommentTextByPostId] = useState({});
  const [commentsByPostId, setCommentsByPostId] = useState({});
  const [visibleSharePostId, setVisibleSharePostId] = useState(null);

  const token = localStorage.getItem("access_token");

  useEffect(() => {
    const fetchFriendsPosts = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/friends/posts/", {
          headers: { Authorization: `Bearer ${token}` },
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

  // Handle like button
  const handleLike = async (postId) => {
    try {
      await axios.post(
        `http://127.0.0.1:8000/posts/${postId}/likes/toggle/`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const response = await axios.get("http://127.0.0.1:8000/friends/posts/", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setPosts(response.data);
    } catch (err) {
      console.error("Error liking post:", err.response?.data || err.message);
    }
  };

  // Handle comment text input
  const handleCommentChange = (postId, value) => {
    setCommentTextByPostId((prev) => ({
      ...prev,
      [postId]: value,
    }));
  };

  // Handle comment submission
  const handleCommentSubmit = async (postId) => {
    const commentText = commentTextByPostId[postId] || "";
    if (!commentText.trim()) return;

    try {
      const res = await axios.post(
        `http://127.0.0.1:8000/posts/${postId}/comments/create/`,
        { text: commentText },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setCommentTextByPostId((prev) => ({
        ...prev,
        [postId]: "",
      }));

      const newComment = res.data;
      setCommentsByPostId((prev) => ({
        ...prev,
        [postId]: [...(prev[postId] || []), newComment],
      }));
    } catch (err) {
      console.error("Error creating comment:", err.response?.data || err.message);
    }
  };

  if (loading) return <p>Loading friends' posts...</p>;
  if (error) return <p className="text-red-500">{error}</p>;

  return (
    <div className="flex flex-col items-center w-full bg-gray-100 p-6">
      <div className="max-w-3xl w-full">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Friends' Posts</h2>

        {posts.length === 0 ? (
          <p className="text-center text-gray-600">No posts from your friends yet.</p>
        ) : (
          <ul className="space-y-6">
            {posts.map((post) => {
              const shareUrl = `${window.location.origin}/post/${post.id}`;

              return (
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
                        {post.author_username || "Unknown User"}
                      </h3>
                      <p className="text-sm text-gray-500">
                        {new Date(post.published).toLocaleString()}
                      </p>
                    </div>
                  </div>

                  {/* Post Content */}
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">{post.title}</h3>
                  <p className="text-gray-700">{post.content}</p>

                  {/* Post Image */}
                  {post.image && (
                    <img src={post.image} alt="Post" className="mt-3 w-full h-auto rounded-lg shadow-md" />
                  )}

                  {/* Like & Share Actions */}
                  <div className="flex justify-between items-center mt-4 text-gray-500 text-sm">
                    <div className="flex gap-4">
                      <button onClick={() => handleLike(post.id)} className="hover:text-pink-500 transition">
                        ❤️ Like
                      </button>
                      <button onClick={() => setVisibleSharePostId(post.id)} className="hover:text-gray-800 transition">
                        🔄 Share
                      </button>
                    </div>
                    <span>{post.likes_count || 0} Likes</span>
                  </div>

                  {/* Share Options */}
                  {visibleSharePostId === post.id && (
                    <div className="flex gap-3 mt-2 flex-wrap">
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText(shareUrl);
                          alert("Link copied to clipboard!");
                        }}
                        className="text-gray-700 hover:underline"
                      >
                        Copy Link
                      </button>
                    </div>
                  )}

                  {/* Comments Section */}
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
                    {(commentsByPostId[post.id] || []).map((comment) => (
                      <div key={comment.id} className="bg-gray-50 p-2 rounded-md mb-1">
                        <strong>{comment.author_username}:</strong> {comment.text}
                      </div>
                    ))}
                  </div>

                  {/* Comment Input Box */}
                  <div className="flex items-center mt-4 gap-2">
                    <img src="/userprofile.png" alt="User" className="w-8 h-8 rounded-full" />
                    <input
                      type="text"
                      placeholder="Write a comment..."
                      className="w-full p-2 bg-gray-100 rounded-full outline-none"
                      value={commentTextByPostId[post.id] || ""}
                      onChange={(e) => handleCommentChange(post.id, e.target.value)}
                    />
                    <button onClick={() => handleCommentSubmit(post.id)} className="text-pink-500 hover:text-pink-600 transition">
                      ➤
                    </button>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}

export default FriendsPosts;

import React, { useEffect, useState } from "react";
import axios from "axios";

// Helper function to build the correct image URL
function getImageUrl(path) {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  if (path.startsWith("/media") || path.startsWith("media")) {
    const normalized = path.replace(/^\/+/, ""); // remove leading slash
    return `http://127.0.0.1:8000/${normalized}`;
  }
  // Fallback: assume the image is stored in the media folder
  return `http://127.0.0.1:8000/media/${path}`;
}

function FriendsPosts() {
  const [posts, setPosts] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  
  // States for comments and share functionality
  const [commentTextByPostId, setCommentTextByPostId] = useState({});
  const [commentsByPostId, setCommentsByPostId] = useState({});
  const [visibleSharePostId, setVisibleSharePostId] = useState(null);

  const token = localStorage.getItem("access_token");
  const API_URL_FRIENDS = "http://127.0.0.1:8000/friends/posts/";

  const fetchFriendsPosts = async () => {
    try {
      const response = await axios.get(API_URL_FRIENDS, {
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

  useEffect(() => {
    if (token) {
      fetchFriendsPosts();
    } else {
      setError("You need to be logged in to view friends' posts.");
      setLoading(false);
    }
  }, [token]);

  // Handle like toggling (re-fetching from the friends posts endpoint afterward)
  const handleLike = async (postId) => {
    try {
      await axios.post(
        `http://127.0.0.1:8000/posts/${postId}/likes/toggle/`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // Re-fetch posts to update like counts using the same API URL for friends posts
      await fetchFriendsPosts();
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
      // Re-fetch friends' posts
      const response = await axios.get(API_URL_FRIENDS, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setPosts(response.data);
    } catch (err) {
      console.error("Error liking comment:", err.response?.data || err.message);
    }
  };

  // Handle comment text changes
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
      // Clear the input for this post
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
    <div>
      <h2 className="text-2xl font-bold mb-4">Friends' Posts</h2>
      {posts.length === 0 ? (
        <p>No posts from your friends yet.</p>
      ) : (
        <ul className="space-y-6">
          {posts.map((post) => {
            // Build share URLs
            const shareUrl = `${window.location.origin}/post/${post.id}`;
            const twitterShareUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(
              shareUrl
            )}&text=${encodeURIComponent(post.title)}`;
            const facebookShareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(
              shareUrl
            )}`;
            const whatsappShareUrl = `https://wa.me/?text=${encodeURIComponent(
              post.title + " " + shareUrl
            )}`;
            const linkedinShareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(
              shareUrl
            )}`;

            return (
              <li key={post.id} className="bg-white p-4 rounded shadow">
                <h3 className="text-xl font-semibold">{post.title}</h3>
                <p className="text-gray-700">{post.content}</p>
                {post.image && (
                  <img
                    src={getImageUrl(post.image)}
                    alt="Post"
                    className="mt-2 w-full h-auto rounded"
                  />
                )}
                <small className="text-gray-500">
                  Published: {new Date(post.published).toLocaleString()}
                </small>
                {/* Social Actions */}
                <div className="flex justify-between items-center mt-4 text-gray-500 text-sm">
                  <div className="flex gap-4">
                    <button
                      onClick={() => handleLike(post.id)}
                      className="hover:text-pink-500 transition"
                    >
                      ❤️ Like
                    </button>
                    <button
                      onClick={() =>
                        setVisibleSharePostId(
                          visibleSharePostId === post.id ? null : post.id
                        )
                      }
                      className="hover:text-gray-800 transition"
                    >
                      🔄 Share
                    </button>
                  </div>
                  <span>{post.likes_count || 0} Likes</span>
                </div>
                {/* Share Options */}
                {visibleSharePostId === post.id && (
                  <div className="flex flex-col gap-2 mt-2 p-3 bg-gray-100 rounded-lg shadow">
                    <span className="text-sm font-semibold">Share this post:</span>
                    <div className="flex gap-3">
                      <a
                        href={twitterShareUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-500 hover:underline"
                      >
                        Twitter
                      </a>
                      <a
                        href={facebookShareUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        Facebook
                      </a>
                      <a
                        href={whatsappShareUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-green-500 hover:underline"
                      >
                        WhatsApp
                      </a>
                      <a
                        href={linkedinShareUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-700 hover:underline"
                      >
                        LinkedIn
                      </a>
                    </div>
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
                    {post.comments?.length > 0 && (
                      <div>
                        {post.comments.map((comment) => (
                          <div key={comment.id} className="bg-gray-50 p-2 rounded-md mb-1 flex items-center justify-between">
                            <dev>
                              <strong>{comment.author_username}:</strong> {comment.text}
                            </dev>
                            
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
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

export default FriendsPosts;

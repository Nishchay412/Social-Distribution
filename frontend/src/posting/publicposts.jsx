import React, { useEffect, useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import { API_BASE_URL } from '../../config';


// Helper function to build the correct image URL
function getImageUrl(path) {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  if (path.startsWith("/media") || path.startsWith("media")) {
    const normalized = path.replace(/^\/+/, "");
    return `${API_BASE_URL}/${normalized}`;
  }
  return `${API_BASE_URL}/media/${path}`;
}

const PublicPosts = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [commentTextByPostId, setCommentTextByPostId] = useState({});
  const [commentsByPostId, setCommentsByPostId] = useState({});
  const [visibleSharePostId, setVisibleSharePostId] = useState(null);

  const API_URL = `${API_BASE_URL}/api/posts/public/`;
  const token = localStorage.getItem("access_token");

  useEffect(() => {
    const fetchPublicPosts = async () => {
      setLoading(true);
      try {
        const response = await axios.get(API_URL, {
          headers: { Authorization: `Bearer ${token}` },
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
  }, [token]);

  // Handle like comment button
  const handleLikeComment = async (postId, commentId) => {
    try {
      await axios.post(
        `${API_BASE_URL}/posts/${postId}/comments/${commentId}/likes/toggle/`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // re-fetch or update local state to show updated like count
      const response = await axios.get(API_URL, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setPosts(response.data);
    } catch (err) {
      console.error("Error liking comment:", err.response?.data || err.message);
    }
  };

  // Handle like button
  const handleLike = async (postId) => {
    try {
      await axios.post(
        `${API_BASE_URL}/posts/${postId}/likes/toggle/`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const response = await axios.get(API_URL, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setPosts(response.data);
    } catch (err) {
      console.error("Error liking post:", err.response?.data || err.message);
    }
  };

  // Handle comment text changes
  const handleCommentChange = (postId, value) => {
    setCommentTextByPostId({
      ...commentTextByPostId,
      [postId]: value,
    });
  };

  // Handle comment submit
  const handleCommentSubmit = async (postId) => {
    const commentText = commentTextByPostId[postId] || "";
    if (!commentText.trim()) return;
    try {
      const res = await axios.post(
        `${API_BASE_URL}/posts/${postId}/comments/create/`,
        { text: commentText },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setCommentTextByPostId({
        ...commentTextByPostId,
        [postId]: "",
      });
      const newComment = res.data;
      setCommentsByPostId((prev) => ({
        ...prev,
        [postId]: [...(prev[postId] || []), newComment],
      }));
    } catch (err) {
      console.error("Error creating comment:", err.response?.data || err.message);
    }
  };

  if (loading) return <p className="text-center text-lg">Loading public posts...</p>;
  if (error) return <p className="text-center text-red-500">{error}</p>;

  return (
    <div className="flex flex-col items-center w-full bg-gray-100 p-6">
      <div className="max-w-3xl w-full">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Public Posts</h2>
        {posts.length === 0 ? (
          <p className="text-center text-gray-600">No public posts available.</p>
        ) : (
          <ul className="space-y-6">
            {posts.map((post) => {
              // Share URLs
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
                  <div className="text-gray-700 markdown-content">
                    <ReactMarkdown>{post.content}</ReactMarkdown>
                  </div>

                  {post.image && (
                    <img
                      src={getImageUrl(post.image)}
                      alt="Post"
                      className="mt-3 w-full h-auto rounded-lg shadow-md"
                    />
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
                  {/* Comment Input */}
                  <div className="flex items-center mt-4 gap-2">
                    <img src="/userprofile.png" alt="User" className="w-8 h-8 rounded-full" />
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
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
};

export default PublicPosts;

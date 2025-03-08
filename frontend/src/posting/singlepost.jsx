import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';

// Helper function to build the correct image URL
function getImageUrl(path) {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  if (path.startsWith("/media") || path.startsWith("media")) {
    const normalized = path.replace(/^\/+/, ""); // remove leading slash
    return `http://127.0.0.1:8000/${normalized}`;
  }
  return `http://127.0.0.1:8000/media/${path}`;
}

function PostDetails() {
  const { id } = useParams();
  
  const [post, setPost] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  
  // State for comment input and share toggle
  const [commentText, setCommentText] = useState("");
  const [visibleShare, setVisibleShare] = useState(false);
  
  const token = localStorage.getItem('access_token');

  useEffect(() => {
    const fetchPost = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/posts/${id}/`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        const data = await response.json();
        if (!response.ok) {
          setError(data.error || 'Failed to fetch the post.');
          return;
        }
        setPost(data);
      } catch (err) {
        console.error(err);
        setError('An error occurred while fetching the post.');
      } finally {
        setLoading(false);
      }
    };

    fetchPost();
  }, [id, token]);

  // Handle like toggling
  const handleLike = async () => {
    try {
      await axios.post(
        `http://127.0.0.1:8000/posts/${id}/likes/toggle/`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // Re-fetch post details to update likes count
      const response = await axios.get(`http://127.0.0.1:8000/posts/${id}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setPost(response.data);
    } catch (err) {
      console.error("Error toggling like:", err.response?.data || err.message);
    }
  };

  // Handle comment submission
  const handleCommentSubmit = async () => {
    if (!commentText.trim()) return;
    try {
      const response = await axios.post(
        `http://127.0.0.1:8000/posts/${id}/comments/create/`,
        { text: commentText },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // Update post comments locally (assumes post.comments is an array)
      setPost(prev => ({ ...prev, comments: [...(prev.comments || []), response.data] }));
      setCommentText("");
    } catch (err) {
      console.error("Error posting comment:", err.response?.data || err.message);
    }
  };

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto p-4">
        <div className="text-gray-600 text-center">Loading post data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto p-4">
        <div className="bg-red-100 text-red-700 p-4 rounded shadow-md text-center">
          Error: {error}
        </div>
      </div>
    );
  }

  if (!post) return null;

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
    <div className="max-w-2xl mx-auto p-4">
      <div className="bg-white shadow-md rounded-lg p-6">
        <h2 className="text-3xl font-bold mb-4 text-gray-800">{post.title}</h2>
        {post.image && (
          <img
            src={getImageUrl(post.image)}
            alt="Post"
            className="mb-4 w-full h-auto rounded"
          />
        )}
        <p className="text-gray-700 mb-4">
          <span className="font-semibold">Content:</span> {post.content}
        </p>
        <div className="flex flex-wrap gap-4 mb-4">
          <p className="text-gray-600">
            <span className="font-semibold">Visibility:</span> {post.visibility}
          </p>
          <p className="text-gray-600">
            <span className="font-semibold">Author:</span> {post.author_username}
          </p>
        </div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex gap-4 items-center">
            <button
              onClick={handleLike}
              className="bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-4 rounded"
            >
              ❤️ Like ({post.likes_count || 0})
            </button>
            <button
              onClick={() => setVisibleShare(!visibleShare)}
              className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded"
            >
              Share
            </button>
          </div>
        </div>
        {visibleShare && (
          <div className="mb-4 p-4 bg-gray-100 rounded">
            <p className="mb-2 font-semibold">Share this post:</p>
            <div className="flex gap-4">
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
              className="mt-2 text-gray-700 hover:underline"
            >
              Copy Link
            </button>
          </div>
        )}
        <Link 
          to={`/profile/${post.author_username}`}
          className="inline-block bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded mb-4"
        >
          View all posts by {post.author_username}
        </Link>
        <div className="mt-4">
          <h3 className="text-2xl font-bold mb-2">Comments</h3>
          {post.comments && post.comments.length > 0 ? (
            <ul className="space-y-2">
              {post.comments.map(comment => (
                <li key={comment.id} className="p-2 bg-gray-50 rounded">
                  <strong>{comment.author_username}:</strong> {comment.text}
                </li>
              ))}
            </ul>
          ) : (
            <p>No comments yet.</p>
          )}
          <div className="mt-4 flex items-center gap-2">
            <img src="/userprofile.png" alt="User" className="w-8 h-8 rounded-full" />
            <input
              type="text"
              placeholder="Write a comment..."
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
              className="w-full p-2 bg-gray-100 rounded-full outline-none"
            />
            <button
              onClick={handleCommentSubmit}
              className="text-pink-500 hover:text-pink-600 transition"
            >
              ➤
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PostDetails;

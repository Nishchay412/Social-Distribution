import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

const PostDetail = () => {
  const { postId } = useParams();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [likes, setLikes] = useState([]);
  const [commentText, setCommentText] = useState("");
  const [error, setError] = useState(null);
  const token = localStorage.getItem("access_token");

  useEffect(() => {
    fetchPost();
    fetchComments();
    fetchLikes();
  }, [postId]);

  const fetchPost = async () => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/posts/${postId}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Failed to load post");
      const data = await res.json();
      setPost(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const fetchComments = async () => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/posts/${postId}/comments/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Failed to load comments");
      const data = await res.json();
      setComments(data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchLikes = async () => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/posts/${postId}/likes/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Failed to load likes");
      const data = await res.json();
      setLikes(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddComment = async () => {
    try {
      const res = await fetch(
        `http://127.0.0.1:8000/posts/${postId}/comments/create/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ text: commentText }),
        }
      );
      if (!res.ok) throw new Error("Failed to add comment");
      setCommentText("");
      fetchComments();
    } catch (err) {
      console.error(err);
    }
  };

  const handleLikePost = async () => {
    try {
      const res = await fetch(
        `http://127.0.0.1:8000/posts/${postId}/likes/create/`,
        {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      if (!res.ok) throw new Error("Failed to like post");
      fetchLikes();
    } catch (err) {
      console.error(err);
    }
  };

  if (error) return <p>Error: {error}</p>;
  if (!post) return <p>Loading post...</p>;

  return (
    <div style={{ maxWidth: "600px", margin: "0 auto", padding: "20px" }}>
      <h2>{post.title}</h2>
      <p>{post.content}</p>
      {post.image && <img src={post.image} alt="Post" style={{ width: "100%" }} />}
      <p>
        <strong>Published:</strong> {new Date(post.published).toLocaleString()}
      </p>
      <button onClick={handleLikePost} style={{ marginBottom: "20px" }}>
        Like
      </button>
      <p>{likes.length} like(s)</p>

      <hr />
      <h3>Comments</h3>
      {comments.length === 0 ? (
        <p>No comments yet.</p>
      ) : (
        <ul>
          {comments.map((comment) => (
            <li key={comment.id}>
              <strong>{comment.author_username}</strong>: {comment.text}
            </li>
          ))}
        </ul>
      )}
      <div style={{ marginTop: "20px" }}>
        <textarea
          value={commentText}
          onChange={(e) => setCommentText(e.target.value)}
          rows={3}
          placeholder="Add a comment..."
          style={{ width: "100%" }}
        />
        <button onClick={handleAddComment} style={{ marginTop: "10px" }}>
          Submit Comment
        </button>
      </div>
    </div>
  );
};

export default PostDetail;
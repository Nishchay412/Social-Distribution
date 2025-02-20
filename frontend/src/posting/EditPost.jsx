import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';

function EditPost() {
  const { postId } = useParams(); // Ensure this is being extracted properly
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [existingImageUrl, setExistingImageUrl] = useState(null);
  const [newImage, setNewImage] = useState(null);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState('');

  const API_BASE_URL = "http://127.0.0.1:8000";

  const getAuthToken = () => {
    const token = localStorage.getItem("access_token");
    return token;
  };

  const fetchPost = async (id) => {
    if (!id) {
      console.error("fetchPost called with undefined postId");
      setError("Invalid post ID.");
      return;
    }

    try {
      console.log("Fetching post with ID:", id);
      const response = await axios.get(`${API_BASE_URL}/posts/${id}/`, {
        headers: {
          "Authorization": `Bearer ${getAuthToken()}`,
        },
      });
      return response.data;
    } catch (error) {
      console.error(`Error fetching post ${id}:`, error.response?.data || error.message);
      setError("Could not load post data.");
    }
  };

  const updatePost = async (id, postData) => {
    if (!id) {
      console.error("updatePost called with undefined postId");
      setError("Invalid post ID.");
      return;
    }

    try {
      console.log("Updating post with ID:", id);
      const response = await axios.put(`${API_BASE_URL}/posts/${id}/update/`, postData, {
        headers: {
          "Authorization": `Bearer ${getAuthToken()}`,
          "Content-Type": "multipart/form-data",
        },
      });
      return response.data;
    } catch (error) {
      console.error(`Error updating post ${id}:`, error.response?.data || error.message);
      setError("Failed to update post.");
    }
  };

  useEffect(() => {
    if (!postId) {
      console.error("No postId found in route params.");
      setError("Invalid post ID.");
      return;
    }

    async function loadPost() {
      const postData = await fetchPost(postId);
      if (postData) {
        setTitle(postData.title);
        setContent(postData.content);
        if (postData.image) {
          setExistingImageUrl(postData.image);
        }
      }
    }
    loadPost();
  }, [postId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!postId) {
      console.error("Attempted to submit with undefined postId");
      setError("Invalid post ID.");
      return;
    }

    try {
      const formData = new FormData();
      formData.append('title', title);
      formData.append('content', content);
      if (newImage) {
        formData.append('image', newImage);
      }

      await updatePost(postId, formData);
      setMessage('Post updated successfully!');
    } catch (err) {
      setError('Failed to update post.');
    }
  };

  if (error) {
    return <div>{error}</div>;
  }

  return (
    <div>
      <h2>Edit Post (ID: {postId || "N/A"})</h2>
      {message && <p style={{ color: 'green' }}>{message}</p>}
      <form onSubmit={handleSubmit}>
        <div>
          <label>Title:</label><br />
          <input 
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </div>
        <div>
          <label>Content:</label><br />
          <textarea
            rows="5"
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
        </div>
        {existingImageUrl && (
          <div>
            <p>Current Image:</p>
            <img src={existingImageUrl} alt="Current" style={{ maxWidth: '200px' }} />
          </div>
        )}
        <div>
          <label>New Image (optional):</label><br />
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setNewImage(e.target.files[0])}
          />
        </div>
        <button type="submit">Update Post</button>
      </form>
    </div>
  );
}

export default EditPost;

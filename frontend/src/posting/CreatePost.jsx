import React, { useState } from 'react';
import axios from 'axios';

function CreatePost() {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState('');

  const API_BASE_URL = "http://127.0.0.1:8000/posts/create/";

  const getAuthToken = () => {
    const token = localStorage.getItem("access_token");
    console.log("Auth Token:", token); // Debugging
    return token;
  };

  const createPost = async (postData) => {
    try {
      const token = getAuthToken();
      if (!token) {
        throw new Error("No authentication token found. Please log in.");
      }

      const response = await axios.post(API_BASE_URL, postData, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "multipart/form-data",
        },
      });

      return response.data;
    } catch (error) {
      console.error("Error creating post:", error.response ? error.response.data : error.message);
      throw error;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      formData.append('title', title);
      formData.append('content', content);
      if (selectedFile) {
        formData.append('image', selectedFile);
      }

      const newPost = await createPost(formData);
      setMessage(`Post created successfully! ID: ${newPost.id}`);
      setTitle('');
      setContent('');
      setSelectedFile(null);
    } catch (err) {
      setError('Failed to create post.');
    }
  };

  return (
    <div>
      <h2>Create a New Post</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {message && <p style={{ color: 'green' }}>{message}</p>}
      <form onSubmit={handleSubmit}>
        <div>
          <label>Title:</label><br />
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Content (plain text or markdown):</label><br />
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows="5"
            required
          />
        </div>
        <div>
          <label>Image (optional):</label><br />
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setSelectedFile(e.target.files[0])}
          />
        </div>
        <button type="submit">Create Post</button>
      </form>
    </div>
  );
}

export default CreatePost;

import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

function EditPost() {
  const { id } = useParams(); // ✅ Extract post ID from the URL
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [existingImageUrl, setExistingImageUrl] = useState(null);
  const [newImage, setNewImage] = useState(null);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState('');

  useEffect(() => {
    async function loadPost() {
      try {
        if (!id) {
          throw new Error("Post ID is missing!");
        }

        const token = localStorage.getItem('access_token');
        if (!token) {
          throw new Error("No authentication token found.");
        }

        const response = await axios.get(`http://127.0.0.1:8000/posts/${id}/`, {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        });

        setTitle(response.data.title);
        setContent(response.data.content);
        if (response.data.image) {
          setExistingImageUrl(response.data.image);
        }
      } catch (err) {
        console.error("Error loading post:", err);
        setError('Could not load post data.');
      }
    }
    loadPost();
  }, [id]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error("No authentication token found.");
      }

      const formData = new FormData();
      formData.append('title', title);
      formData.append('content', content);
      if (newImage) {
        formData.append('image', newImage);
      }

      await axios.put(`http://127.0.0.1:8000/posts/${id}/update/`, formData, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "multipart/form-data",
        }
      });

      setMessage('Post updated successfully!');
    } catch (err) {
      console.error("Error updating post:", err);
      setError('Failed to update post.');
    }
  };

  return (
    <div>
      <h2>Edit Post (ID: {id})</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {message && <p style={{ color: 'green' }}>{message}</p>}
      <form onSubmit={handleSubmit}>
        <div>
          <label>Title:</label><br/>
          <input 
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </div>
        <div>
          <label>Content:</label><br/>
          <textarea
            rows="5"
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
        </div>
        {existingImageUrl && (
          <div>
            <p>Current Image:</p>
            <img src={existingImageUrl} alt="Current" style={{ maxWidth: '200px' }}/>
          </div>
        )}
        <div>
          <label>New Image (optional):</label><br/>
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

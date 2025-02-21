import React, { useState } from 'react';
import axios from 'axios';

function CreatePost() {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [visibility, setVisibility] = useState('PUBLIC');  // ✅ Default to PUBLIC
  const [error, setError] = useState(null);
  const [message, setMessage] = useState('');

  const API_BASE_URL = "http://127.0.0.1:8000/posts/create/";  // ✅ Ensure correct API endpoint

  const getAuthToken = () => localStorage.getItem("access_token");

  const createPost = async (postData) => {
    try {
      const token = getAuthToken();
      if (!token) throw new Error("No authentication token found. Please log in.");

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
      formData.append('visibility', visibility);  // ✅ Include visibility option
      if (selectedFile) formData.append('image', selectedFile);

      const newPost = await createPost(formData);
      setMessage(`Post created successfully! ID: ${newPost.id}`);
      setTitle('');
      setContent('');
      setSelectedFile(null);
      setVisibility('PUBLIC');  // ✅ Reset to default visibility
      setError(null);
    } catch (err) {
      setError('Failed to create post.');
      setMessage('');
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-6">
      <div className="bg-white p-8 rounded-2xl shadow-xl max-w-lg w-full">
        <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">Create a New Post</h2>
        
        {error && <p className="text-red-600 bg-red-100 p-3 rounded-md text-sm mb-4">{error}</p>}
        {message && <p className="text-green-600 bg-green-100 p-3 rounded-md text-sm mb-4">{message}</p>}
        
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-gray-700 font-medium mb-2">Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-gray-700 font-medium mb-2">Content (Markdown supported)</label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows="5"
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-gray-700 font-medium mb-2">Image (Optional)</label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setSelectedFile(e.target.files[0])}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-gray-700 font-medium mb-2">Visibility</label>
            <select
              value={visibility}
              onChange={(e) => setVisibility(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="PUBLIC">Public</option>
              <option value="PRIVATE">Private</option>
            </select>
          </div>
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
          >
            Create Post
          </button>
        </form>
      </div>
    </div>
  );
}

export default CreatePost;

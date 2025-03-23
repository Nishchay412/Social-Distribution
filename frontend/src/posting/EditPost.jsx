import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../../config';

function EditPost() {
    const { postId } = useParams(); // ✅ Ensure this matches your router
    const navigate = useNavigate();
    
    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');
    const [existingImageUrl, setExistingImageUrl] = useState(null);
    const [newImage, setNewImage] = useState(null);
    const [error, setError] = useState(null);
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function loadPost() {
            setLoading(true);
            try {
                if (!postId) throw new Error("Post ID is missing!");
                
                const token = localStorage.getItem('access_token');
                if (!token) throw new Error("No authentication token found.");

                const response = await axios.get(`${API_BASE_URL}/api/posts/${postId}/`, {
                    headers: { "Authorization": `Bearer ${token}` }
                });

                setTitle(response.data.title);
                setContent(response.data.content);
                if (response.data.image) setExistingImageUrl(response.data.image);
            } catch (err) {
                console.error("Error loading post:", err);
                setError('Could not load post data.');
            } finally {
                setLoading(false);
            }
        }
        loadPost();
    }, [postId]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('access_token');
            if (!token) throw new Error("No authentication token found.");

            const formData = new FormData();
            formData.append('title', title);
            formData.append('content', content);
            if (newImage) {
                formData.append('image', newImage);
            }

            await axios.put(`${API_BASE_URL}/api/posts/${postId}/update/`, formData, {
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "multipart/form-data",
                }
            });

            setMessage('Post updated successfully!');
            setTimeout(() => navigate("/my-posts"), 2000);  // ✅ Redirect after 2s
        } catch (err) {
            console.error("Error updating post:", err);
            setError('Failed to update post.');
        }
    };

    if (loading) return <p>Loading post...</p>;

    return (
        <div>
            <h2>Edit Post (ID: {postId})</h2>
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

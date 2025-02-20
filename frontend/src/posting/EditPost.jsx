import React, { useEffect, useState } from 'react';
import { fetchPost, updatePost } from './profileService';
import { useParams } from 'react-router-dom'; 

function EditPost() {
  const { postId } = useParams(); // from route like /posts/:postId/edit
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [existingImageUrl, setExistingImageUrl] = useState(null);
  const [newImage, setNewImage] = useState(null);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState('');

  useEffect(() => {
    async function loadPost() {
      try {
        const postData = await fetchPost(postId);
        setTitle(postData.title);
        setContent(postData.content);
        if (postData.image) {
          // e.g. postData.image might be "/media/images/...jpg"
          setExistingImageUrl(postData.image);
        }
      } catch (err) {
        console.error(err);
        setError('Could not load post data.');
      }
    }
    loadPost();
  }, [postId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // If we want to handle images, use FormData again
      const formData = new FormData();
      formData.append('title', title);
      formData.append('content', content);
      if (newImage) {
        formData.append('image', newImage);
      }

      const updated = await updatePost(postId, formData);
      setMessage('Post updated successfully!');
    } catch (err) {
      console.error(err);
      setError('Failed to update post.');
    }
  };

  if (error) {
    return <div>{error}</div>;
  }

  return (
    <div>
      <h2>Edit Post (ID: {postId})</h2>
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
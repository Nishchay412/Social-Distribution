import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';

function PostDetails() {
  // "id" will be taken from the URL defined in your route "/post/:id"
  const { id } = useParams();
  
  const [post, setPost] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchPost = async () => {
      try {
        // Retrieve the token (if you're using token-based auth)
        const token = localStorage.getItem('access_token');

        // Make the fetch call to your Django backend
        const response = await fetch(`http://127.0.0.1:8000/posts/${id}/`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        // Parse the JSON response
        const data = await response.json();

        // Check for HTTP errors
        if (!response.ok) {
          setError(data.error || 'Failed to fetch the post.');
          return;
        }

        // If successful, store the post data
        setPost(data);
      } catch (err) {
        console.error(err);
        setError('An error occurred while fetching the post.');
      }
    };

    // Call the async function
    fetchPost();
  }, [id]);

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!post) {
    return <div>Loading post data...</div>;
  }

  return (
    <div>
      <h2>{post.title}</h2>
      <p><strong>Content:</strong> {post.content}</p>
      <p><strong>Visibility:</strong> {post.visibility}</p>
      <p><strong>Author:</strong> {post.author_username}</p>

      {/* Link to view all posts by the user */}
      <Link to={`/profile/${post.author_username}`}>
        View all posts by {post.author_username}
      </Link>
    </div>
  );
}

export default PostDetails;

import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';

function PostDetails() {
  const { id } = useParams();
  
  const [post, setPost] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchPost = async () => {
      try {
        const token = localStorage.getItem('access_token');
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
      }
    };

    fetchPost();
  }, [id]);

  if (error) {
    return (
      <div className="max-w-2xl mx-auto p-4">
        <div className="bg-red-100 text-red-700 p-4 rounded shadow-md text-center">
          Error: {error}
        </div>
      </div>
    );
  }

  if (!post) {
    return (
      <div className="max-w-2xl mx-auto p-4">
        <div className="text-gray-600 text-center">Loading post data...</div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-4">
      <div className="bg-white shadow-md rounded-lg p-6">
        <h2 className="text-3xl font-bold mb-4 text-gray-800">{post.title}</h2>
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
        <Link 
          to={`/profile/${post.author_username}`}
          className="inline-block bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded"
        >
          View all posts by {post.author_username}
        </Link>
      </div>
    </div>
  );
}

export default PostDetails;

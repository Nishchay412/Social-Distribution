import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import { API_BASE_URL } from '../../config';
const UserPosts = () => {
    const { username } = useParams();
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchPosts = async () => {
            setLoading(true);
            const token = localStorage.getItem("access_token");

            try {
                const response = await fetch(`http://127.0.0.1:8000/api/posts/user/${username}/`, {
                    headers: { Authorization: `Bearer ${token}` },
                });

                if (!response.ok) {
                    throw new Error("Failed to fetch posts");
                }

                const data = await response.json();
                setPosts(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchPosts();
    }, [username]);

    if (loading) return <p className="text-center text-gray-500">Loading posts...</p>;
    if (error) return <p className="text-center text-red-500">Error: {error}</p>;

    return (
        <div className="max-w-3xl mx-auto p-6 bg-white shadow-md rounded-lg">
            <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">{username}'s Posts</h2>
            {posts.length === 0 ? (
                <p className="text-center text-gray-500">No posts found.</p>
            ) : (
                <ul className="space-y-6">
                    {posts.map((post) => (
                        <li key={post.id} className="border-b border-gray-200 pb-4">
                            <h3 className="text-xl font-semibold text-gray-700">{post.title}</h3>
                            <div className="text-gray-700 markdown-content">
                                <ReactMarkdown>{post.content}</ReactMarkdown>
                            </div>
                            {post.image && <img src={post.image} alt="Post" className="w-full mt-4 rounded-lg" />}
                            <p className="text-sm text-gray-400 mt-2"><strong>Published:</strong> {new Date(post.published).toLocaleString()}<strong>Last Edited:</strong> {new Date(post.updated).toLocaleString()}</p>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default UserPosts;
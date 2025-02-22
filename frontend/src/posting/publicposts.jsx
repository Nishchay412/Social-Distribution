import React, { useEffect, useState } from "react";
import axios from "axios";

const PublicPosts = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const API_URL = "http://127.0.0.1:8000/api/posts/public/";

  useEffect(() => {
    const fetchPublicPosts = async () => {
      setLoading(true);
      const token = localStorage.getItem("access_token"); // Get JWT token

      try {
        const response = await axios.get(API_URL, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        setPosts(response.data);
      } catch (err) {
        setError("Failed to fetch public posts.");
        console.error("Error fetching posts:", err.response?.data || err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPublicPosts();
  }, []);

  if (loading) return <p className="text-center text-lg">Loading public posts...</p>;
  if (error) return <p className="text-center text-red-500">{error}</p>;

  return (
    <div className="flex flex-col items-center w-full bg-gray-100 p-6">
      <div className="max-w-3xl w-full">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Public Posts</h2>

        {posts.length === 0 ? (
          <p className="text-center text-gray-600">No public posts available.</p>
        ) : (
          <ul className="space-y-6">
            {posts.map((post) => (
              <li key={post.id} className="bg-white p-5 rounded-2xl shadow-md">
                {/* Post Header */}
                <div className="flex items-center gap-3 mb-3">
                  <img
                    src={post.author_profile_pic || "/default-avatar.png"}
                    alt="User"
                    className="w-10 h-10 rounded-full"
                  />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800">{post.author_username}</h3>
                    <p className="text-sm text-gray-500">{new Date(post.published).toLocaleString()}</p>
                  </div>
                </div>

                {/* Post Content */}
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{post.title}</h3>
                <p className="text-gray-700">{post.content}</p>

                {/* Post Image */}
                {post.image && (
                  <img
                    src={post.image}
                    alt="Post"
                    className="mt-3 w-full h-auto rounded-lg shadow-md"
                  />
                )}

                {/* Social Actions */}
                <div className="flex justify-between items-center mt-4 text-gray-500 text-sm">
                  <div className="flex gap-4">
                    <button className="flex items-center gap-1 hover:text-pink-500 transition">
                      ❤️ Like
                    </button>
                    <button className="flex items-center gap-1 hover:text-blue-500 transition">
                      💬 Comment
                    </button>
                    <button className="flex items-center gap-1 hover:text-gray-800 transition">
                      🔄 Share
                    </button>
                  </div>
                  <span>{post.likes} Likes</span>
                </div>

                {/* Comment Input */}
                <div className="flex items-center mt-4 gap-2">
                  <img
                    src="/userprofile.png"
                    alt="User"
                    className="w-8 h-8 rounded-full"
                  />
                  <input
                    type="text"
                    placeholder="Write a comment..."
                    className="w-full p-2 bg-gray-100 rounded-full outline-none"
                  />
                  <button className="text-pink-500 hover:text-pink-600 transition">
                    ➤
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
export default PublicPosts
import React from "react";
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { API_BASE_URL } from '../../config';

export function CreatePost1(){
    
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [visibility, setVisibility] = useState('PUBLIC');  // ✅ Default to PUBLIC
  const [error, setError] = useState(null);
  const [message, setMessage] = useState('');
    const API_BASE_URL = "${API_BASE_URL}/posts/create/";  // ✅ Ensure correct API endpoint

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

    const profilepic = localStorage.getItem("profilepic")
    const first_name = localStorage.getItem("firstname")
    
    return(
        <div className="flex flex-col bg-gray-300 rounded-2xl items-center">
            <div className="flex gap-4 ">
                <img src ={profilepic} className="w-12 h-12 rounded-4xl mt-4">
                </img>
                <div className="flex flex-col gap-2">
                <input type ="text" placeholder="Title " 
                onChange={(e) => setTitle(e.target.value)}
                value={title}
                    className="w-full p-2 bg-gray-100 rounded-full outline-none"> 
                    </input>
                    <input type="text" placeholder={`What's happening, ${first_name}?`}
                    value = {content}
                    onChange={(e) => setContent(e.target.value)} 
                    className="w-full p-2 bg-gray-100 rounded-full outline-none"/> 
    
                </div>
                

            </div>
            <div className="mt-2 flex gap-3">
                <img src ="/image.png " className="w-6 h-6 rounded-sm">
                </img>
                <img>
                </img>
                <img>
                </img>
            </div>


        </div>
    )
}
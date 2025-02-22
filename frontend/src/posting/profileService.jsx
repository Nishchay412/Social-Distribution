import axios from 'axios';

// Base API client with interceptors
const apiClient = axios.create({
  baseURL: "http://127.0.0.1:8000",  // Adjust if using a different backend URL
  headers: {
    "Content-Type": "application/json",
  },
});
export async function toggleLike(postId) {
  try {
    const response = await apiClient.post(`/posts/${postId}/likes/toggle/`, {});
    return response.data;
  } catch (error) {
    console.error(`Error toggling like for post ${postId}:`, error.response?.data || error.message);
    throw error;
  }
}
// Helper function to get JWT token from localStorage
function getAuthToken() {
  return localStorage.getItem('access') || null;
}

// Attach Authorization header using an interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Function to create a new post
export async function createPost(postData) {
  try {
    const response = await apiClient.post("/posts/create/", postData, {
      headers: { "Content-Type": "multipart/form-data" }, // Ensures correct handling of files
    });
    return response.data;
  } catch (error) {
    console.error("Error creating post:", error.response?.data || error.message);
    throw error;
  }
}

// Function to fetch all authors
export async function fetchAuthors() {
  try {
    const response = await apiClient.get("/authors/");
    return response.data;
  } catch (error) {
    console.error("Error fetching authors:", error.response?.data || error.message);
    throw error;
  }
}

// Function to fetch a single post
export async function fetchPost(postId) {
  try {
    const response = await apiClient.get(`/posts/${postId}/`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching post ${postId}:`, error.response?.data || error.message);
    throw error;
  }
}

// Function to update an existing post
export async function updatePost(postId, postData) {
  try {
    const response = await apiClient.put(`/posts/${postId}/update/`, postData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  } catch (error) {
    console.error(`Error updating post ${postId}:`, error.response?.data || error.message);
    throw error;
  }
}

// Function to fetch all posts
export async function fetchPosts() {
  try {
    const response = await apiClient.get("/posts/");
    return response.data;
  } catch (error) {
    console.error("Error fetching posts:", error.response?.data || error.message);
    throw error;
  }
}

// Alternative function to create a new post using Fetch API
export async function createPostFetch(postData) {
  try {
    const token = getAuthToken();
    const response = await fetch("http://127.0.0.1:8000/posts/create/", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
      body: postData, // Automatically sets correct content type for FormData
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Error creating post:", error.message);
    throw error;
  }
}

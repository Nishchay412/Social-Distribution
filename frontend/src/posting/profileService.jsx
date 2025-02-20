import axios from 'axios';

// Create a helper function to get the JWT token from localStorage
function getAuthToken() {
  return localStorage.getItem('access') || null;
}

const token = getAuthToken();
const response = await fetch("http://127.0.0.1:8000/posts/create/", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${token}`,
  },
  body: someFormDataOrJson,
});

// Add an interceptor to attach Authorization headers
apiClient.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Example: fetch all authors
export async function fetchAuthors() {
  const response = await apiClient.get('/authors/');
  return response.data;  // adjust if your API shape is different
}

// Example: fetch a single post
export async function fetchPost(postId) {
  const response = await apiClient.get(`/posts/${postId}/`);
  return response.data;
}

// Example: create a new post
export async function createPost(postData) {
  // postData could be a FormData if uploading images,
  // or a JSON object for plain text
  const response = await apiClient.post('/posts/create/', postData);
  return response.data;
}

// Example: update a post
export async function updatePost(postId, postData) {
  const response = await apiClient.put(`/posts/${postId}/update/`, postData);
  return response.data;
}

// Example: get all posts
export async function fetchPosts() {
  const response = await apiClient.get('/posts/');
  return response.data;
}


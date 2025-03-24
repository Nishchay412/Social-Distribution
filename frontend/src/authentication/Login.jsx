import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { API_BASE_URL } from "../../config";

export default function Login() {
  const [formData, setFormData] = useState({
    username: "",
    password: ""
  });
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const navigate = useNavigate();

  const navigate_login = () => {
    navigate("/sign-up");
  };
  const navigate_dashboard = () => {
    navigate("/dashboard");
  };
  const navigate_admin_dashboard = () => {
    navigate("/admin-dashboard");
  };

  // Handle input changes
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch(`${API_BASE_URL}/login/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (!response.ok) {
        console.error("Server Response:", data);
        setError(data.error || "Login failed. Please check your credentials.");
      } else {
        setSuccess("Login successful! 🎉");
        
        if (data.user.admin) {
          setSuccess("Admin Detected 🔐");
          navigate_admin_dashboard();
        } else {
          setSuccess("Login successful! 🎉");
          navigate_dashboard();
        }
        
        localStorage.setItem("username", data.user.username);
        localStorage.setItem("firstname", data.user.first_name);
        localStorage.setItem("lastname", data.user.last_name);
        localStorage.setItem("email", data.user.email);
        localStorage.setItem("profilepic", data.user.profile_image);

        // Store JWT Tokens in localStorage for authentication
        localStorage.setItem("access_token", data.access);
        localStorage.setItem("refresh_token", data.refresh);
      }
    } catch (error) {
      console.error("Network error:", error);
      setError("Something went wrong. Please try again.");
    }
  };

  return (
    <div className="flex justify-center items-center min-h-screen">
      <div className="border-2 p-12 rounded shadow-lg flex flex-col items-center w-96">
        <h2 className="text-2xl font-bold mb-4">Login</h2>
        {error && <p className="text-red-500">{error}</p>}
        {success && <p className="text-green-500">{success}</p>}
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <input 
            name="username"
            type="text"
            placeholder="Username"
            value={formData.username}
            onChange={handleChange}
            className="border p-2 rounded"
            required
          />
          <input 
            name="password"
            type="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            className="border p-2 rounded"
            required
          />
          <button 
            type="submit"
            className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
          >
            Login
          </button>
          <div className="flex items-center justify-center gap-2">
            <h1 className="mt-2">New User?</h1>
            <button 
              className="py-2 mt-2 text-blue-500 cursor-pointer"
              onClick={navigate_login}
            >
              Sign UP
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

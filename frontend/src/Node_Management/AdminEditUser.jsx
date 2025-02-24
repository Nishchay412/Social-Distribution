import React, { useState } from "react";


function Admin_Edit_User({ onClose, user }) {
  const [error, setError] = useState(null);
  const accessToken = localStorage.getItem("access_token");

  const [formData, setFormData] = useState({
    username: user.username,
    firstname: user.first_name,
    lastname: user.last_name,
    email: user.email,
    profile_picture: user.profile_picture || "https://via.placeholder.com/150?text=User",
  });

  // Handle Form Input Changes
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Handle Image Upload
  const handleImageUpload = (event) => {
    const file = event.target.files[0];

    if (file) {
      const reader = new FileReader();
      reader.readAsDataURL(file);

      reader.onload = () => {
        setFormData({ ...formData, profile_picture: reader.result });
      };

      reader.onerror = () => {
        setError("Failed to upload image");
      };
    }
  };

  // Handle Form Submission
  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent default form submission
    try {
      const formDataToSend = new FormData();
      formDataToSend.append("username", formData.username);
      formDataToSend.append("first_name", formData.firstname);
      formDataToSend.append("last_name", formData.lastname);
      formDataToSend.append("email", formData.email);

      if (formData.profile_picture.startsWith("data:image")) {
        const blob = await fetch(formData.profile_picture).then((res) => res.blob());
        formDataToSend.append("profile_picture", blob, "profile.jpg");
      }

      const response = await fetch(
        `http://127.0.0.1:8000/users/exclude-self/${user.username}/update-user/`,  // ✅ Fixed API URL
        {
          method: "PATCH",
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
          body: formDataToSend,
        }
      );
      

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Update error:", response.status, errorText);
        throw new Error(`Update failed: ${response.status} ${errorText}`);
      }

      const updatedData = await response.json();
      setFormData({
        username: updatedData.user.username,
        firstname: updatedData.user.first_name,
        lastname: updatedData.user.last_name,
        email: updatedData.user.email,
        profile_picture: updatedData.user.profile_picture || "https://via.placeholder.com/150?text=User",
      });
    } catch (err) {
      console.error("Update error:", err);
      setError("Failed to update profile");
    }
  };

  return (
    <div className="fixed inset-0 backdrop-blur-sm flex justify-center items-center">
      <div className="mt-10 flex flex-col gap-5">
        <button onClick={onClose} className="place-self-end">
          ❌
        </button>
        <div className="bg-white rounded-xl px-20 py-10 flex flex-col gap-5 items-center mx-4">
          <h1 className="bg-blue-500 text-2xl font-extrabold text-white">Admin - Edit User</h1>
          <form className="text-left w-full space-y-2" onSubmit={handleSubmit}>
            <strong>Profile Pic</strong>
            <input
              type="file"
              accept="image/*"
              className="mt-2"
              onChange={handleImageUpload}
            />

            {/* Show Preview of Uploaded Image */}
            <div className="mt-2">
              <img
                src={formData.profile_picture}
                alt="Profile Preview"
                className="w-24 h-24 rounded-full object-cover border border-gray-300"
              />
            </div>

            <strong>Username</strong>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              className="border p-1 rounded w-full"
            />

            <strong>First Name</strong>
            <input
              type="text"
              name="firstname"
              value={formData.firstname}
              onChange={handleChange}
              className="border p-1 rounded w-full"
            />

            <strong>Last Name</strong>
            <input
              type="text"
              name="lastname"
              value={formData.lastname}
              onChange={handleChange}
              className="border p-1 rounded w-full"
            />

            <strong>Email</strong>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="border p-1 rounded w-full"
            />

            <button
              type="submit"
              className="mt-4 px-4 py-2 items-center text-white font-medium rounded-md bg-blue-500 hover:bg-blue-600"
            >
              Submit
            </button>
          </form>
          {error && (
            <p className="text-red-600 bg-red-100 p-2 rounded-md text-sm mt-3">
              {error}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default Admin_Edit_User;

import React, { useState, useEffect } from "react";

export function User_Profile() {
    const [formData, setFormData] = useState({
        username: "",
        firstname: "",
        lastname: "",
        email: "",
        profile_picture: "https://via.placeholder.com/150?text=User",  // ✅ Default Image
    });

    const [isEditing, setIsEditing] = useState(false);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);
    
    const accessToken = localStorage.getItem("access_token"); // ✅ Get token

    // ✅ Fetch User Data from API on Page Load
    useEffect(() => {
        const fetchUserProfile = async () => {
            try {
                const username = localStorage.getItem("username"); // ✅ Get username from storage
                if (!username) throw new Error("No username found in localStorage");
    
                const response = await fetch(`http://127.0.0.1:8000/profile/${username}/`, {
                    headers: {
                        "Authorization": `Bearer ${accessToken}`,  // ✅ Add JWT token
                    },
                });
    
                if (!response.ok) throw new Error("Failed to fetch user data");
    
                const data = await response.json();
                console.log("Fetched User:", data);
    
                setFormData({
                    username: data.username,
                    firstname: data.first_name,
                    lastname: data.last_name,
                    email: data.email,
                    profile_picture: data.profile_picture || "https://via.placeholder.com/150?text=User",
                });
    
                setLoading(false);
            } catch (err) {
                console.error("Fetch error:", err);
                setError("Failed to load profile");
                setLoading(false);
            }
        };
    
        if (accessToken) {
            fetchUserProfile();
        } else {
            setError("User not authenticated");
            setLoading(false);
        }
    }, [accessToken]);
    

    // ✅ Handle Input Changes
    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    // ✅ Handle Profile Image Upload
    const handleImageUpload = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                setFormData({ ...formData, profile_picture: event.target.result });
            };
            reader.readAsDataURL(file);
        }
    };

    // ✅ Handle Save Button (Send Updated Data to API)
    const handleSave = async (username) => {
        try {
            const formDataToSend = new FormData();
            formDataToSend.append("username", formData.username);
            formDataToSend.append("first_name", formData.firstname);
            formDataToSend.append("last_name", formData.lastname);
            formDataToSend.append("email", formData.email);

            if (formData.profile_picture.startsWith("data:image")) {
                const blob = await fetch(formData.profile_picture).then(res => res.blob());
                formDataToSend.append("profile_picture", blob, "profile.jpg");
            }

            const response = await fetch("http://127.0.0.1:8000/update-profile/", {
                method: "PATCH",
                headers: {
                    "Authorization": `Bearer ${accessToken}`,
                },
                body: formDataToSend,
            });

            if (!response.ok) throw new Error("Update failed");

            const updatedData = await response.json();
            setFormData({
                username: updatedData.user.username,
                firstname: updatedData.user.first_name,
                lastname: updatedData.user.last_name,
                email: updatedData.user.email,
                profile_picture: updatedData.user.profile_picture || "https://via.placeholder.com/150?text=User",
            });

            setIsEditing(false); // ✅ Exit edit mode
        } catch (err) {
            console.error("Update error:", err);
            setError("Failed to update profile");
        }
    };

    if (loading) return <p>Loading...</p>;
    if (error) return <p className="text-red-500">{error}</p>;

    return (
        <div className="flex justify-center items-center min-h-screen">
            <div className="border-2 p-12 rounded shadow-lg flex flex-col items-center w-96">
                <h2 className="text-2xl font-bold mb-4">User Profile</h2>

                {/* ✅ Profile Image Section */}
                <div className="mb-4 flex flex-col items-center">
                    <img
                        src={formData.profile_picture}
                        alt="Profile"
                        className="w-24 h-24 rounded-full border-2 border-gray-300"
                    />
                    {isEditing && (
                        <input
                            type="file"
                            accept="image/*"
                            className="mt-2"
                            onChange={handleImageUpload}
                        />
                    )}
                </div>

                {/* ✅ User Information */}
                <div className="text-left w-full space-y-2">
                    <div>
                        <strong>Username:</strong>
                        {isEditing ? (
                            <input 
                                type="text" 
                                name="username"
                                value={formData.username} 
                                onChange={handleChange}
                                className="border p-1 rounded w-full"
                            />
                        ) : (
                            <span className="ml-2">{formData.username}</span>
                        )}
                    </div>

                    <div>
                        <strong>First Name:</strong> 
                        {isEditing ? (
                            <input 
                                type="text" 
                                name="firstname"
                                value={formData.firstname} 
                                onChange={handleChange}
                                className="border p-1 rounded w-full"
                            />
                        ) : (
                            <span className="ml-2">{formData.firstname}</span>
                        )}
                    </div>

                    <div>
                        <strong>Last Name:</strong> 
                        {isEditing ? (
                            <input 
                                type="text" 
                                name="lastname"
                                value={formData.lastname} 
                                onChange={handleChange}
                                className="border p-1 rounded w-full"
                            />
                        ) : (
                            <span className="ml-2">{formData.lastname}</span>
                        )}
                    </div>

                    <div>
                        <strong>Email:</strong> 
                        {isEditing ? (
                            <input 
                                type="email" 
                                name="email"
                                value={formData.email} 
                                onChange={handleChange}
                                className="border p-1 rounded w-full"
                            />
                        ) : (
                            <span className="ml-2">{formData.email}</span>
                        )}
                    </div>
                </div>

                {/* ✅ Edit/Save Button */}
                <button 
                    className={`mt-4 p-2 rounded ${isEditing ? 'bg-green-500 hover:bg-green-600' : 'bg-blue-500 hover:bg-blue-600'} text-white`}
                    onClick={() => isEditing ? handleSave(localStorage.getItem("username")) : setIsEditing(true)}
                >
                    {isEditing ? "Save" : "Edit"}
                </button>
            </div>
        </div>
    );
}

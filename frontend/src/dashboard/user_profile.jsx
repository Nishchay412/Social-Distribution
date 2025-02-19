import React, { useState } from "react";

export function User_Profile() {
    // ✅ Get user data from localStorage
    const [formData, setFormData] = useState({
        username: localStorage.getItem("username") || "",
        firstname: localStorage.getItem("firstname") || "",
        lastname: localStorage.getItem("lastname") || "",
        email: localStorage.getItem("email") || ""
    });

    // ✅ Track if user is in edit mode
    const [isEditing, setIsEditing] = useState(false);

    // ✅ Handle input changes
    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    // ✅ Toggle Edit/Save button
    const handleEditToggle = () => {
        if (isEditing) {
            // ✅ If saving, store the updated data in localStorage
            localStorage.setItem("username", formData.username);
            localStorage.setItem("firstname", formData.firstname);
            localStorage.setItem("lastname", formData.lastname);
            localStorage.setItem("email", formData.email);
        }
        setIsEditing(!isEditing);  // ✅ Toggle editing state
    };

    return (
        <div className="flex justify-center items-center min-h-screen">
            <div className="border-2 p-12 rounded shadow-lg flex flex-col items-center w-96">
                <h2 className="text-2xl font-bold mb-4">User Profile</h2>
                
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
                
                <button 
                    className={`mt-4 p-2 rounded ${isEditing ? 'bg-green-500 hover:bg-green-600' : 'bg-blue-500 hover:bg-blue-600'} text-white`}
                    onClick={handleEditToggle}   // ✅ Toggle Edit/Save on click
                >
                    {isEditing ? "Save" : "Edit"}
                </button>
            </div>
        </div>
    );
}

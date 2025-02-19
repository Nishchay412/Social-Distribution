import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Signup() {
    const [formData, setFormData] = useState({
        first_name: "",
        last_name: "",
        email: "",
        username: "",
        password: ""
    });

    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    // ✅ Correct use of useNavigate
    const navigate = useNavigate();  // Hook at the top level

    // ✅ Correct navigate_signup function
    const navigate_signup = () => {
        navigate("/login");  // ✅ Call navigate to go to /login
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
            const response = await fetch("http://127.0.0.1:8000/register/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(formData)
            });
    
            const data = await response.json();
    
            if (!response.ok) {
                console.error("Server Response:", data); // Log the error details
                setError(data.error || "Registration failed. Please check your inputs.");
            } else {
                setSuccess("User registered successfully! 🎉");
                setFormData({ first_name: "", last_name: "", email: "", username: "", password: "" });

                // ✅ Automatically navigate to login after successful signup
                setTimeout(() => {
                    navigate("/login");
                }, 2000);  // Delay for user to see success message
            }
        } catch (error) {
            console.error("Network error:", error);
            setError("Something went wrong. Please try again.");
        }
    };

    return (
        <div className="flex justify-center items-center min-h-screen">
            <div className="border-2 p-12 rounded shadow-lg flex flex-col items-center w-96">
                <h2 className="text-2xl font-bold mb-4">Sign Up</h2>
                
                {error && <p className="text-red-500">{error}</p>}
                {success && <p className="text-green-500">{success}</p>}

                <form onSubmit={handleSubmit} className="flex flex-col gap-3">
                    <input 
                        name="first_name"
                        type="text"
                        placeholder="First Name"
                        value={formData.first_name}
                        onChange={handleChange}
                        className="border p-2 rounded"
                        required
                    />
                    <input 
                        name="last_name"
                        type="text"
                        placeholder="Last Name"
                        value={formData.last_name}
                        onChange={handleChange}
                        className="border p-2 rounded"
                        required
                    />
                    <input 
                        name="email"
                        type="email"
                        placeholder="Email"
                        value={formData.email}
                        onChange={handleChange}
                        className="border p-2 rounded"
                        required
                    />
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
                        Sign Up
                    </button>
                    <div className="flex gap-2 ">
                        <h1 className="mt-2">
                            Already a User? 
                        </h1>
                        <button 
                            className="py-2 text-blue-500 cursor-pointer"
                            onClick={navigate_signup}   // ✅ Correct use of navigate_signup
                        >
                            Log In
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

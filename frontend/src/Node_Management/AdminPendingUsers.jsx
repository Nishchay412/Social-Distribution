import React, { useEffect, useState } from "react";

const AdminPendingUsers = () => {
  const [pendingUsers, setPendingUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Retrieve admin token from local storage
  const token = localStorage.getItem("access_token");

  // Function to fetch pending users from the backend
  const fetchPendingUsers = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await fetch("http://127.0.0.1:8000/api/admin/pending-users/", {
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}` // or use Bearer if using JWT
        },
      });
      if (!response.ok) {
        throw new Error("Failed to fetch pending users");
      }
      const data = await response.json();
      setPendingUsers(data);
    } catch (err) {
      console.error(err);
      setError("Error fetching pending users.");
    } finally {
      setLoading(false);
    }
  };

  // Function to approve a specific user
  const approveUser = async (userId) => {
    setError("");
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/admin/approve-user/${userId}/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}` // or Bearer if using JWT
        },
      });
      if (!response.ok) {
        throw new Error("Failed to approve user");
      }
      // Refresh the list after approval
      fetchPendingUsers();
    } catch (err) {
      console.error(err);
      setError("Error approving user.");
    }
  };

  // Fetch pending users on component mount
  useEffect(() => {
    fetchPendingUsers();
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Pending User Approvals</h1>
      {loading && <p>Loading pending users...</p>}
      {error && <p className="text-red-500">{error}</p>}
      {!loading && pendingUsers.length === 0 && <p>No pending users.</p>}
      <ul>
        {pendingUsers.map((user) => (
          <li key={user.id} className="border p-4 mb-2 rounded flex justify-between items-center">
            <div>
              <p className="font-medium">{user.username}</p>
              <p className="text-sm text-gray-600">{user.email}</p>
            </div>
            <button
              className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600"
              onClick={() => approveUser(user.username)}
            >
              Approve
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default AdminPendingUsers;

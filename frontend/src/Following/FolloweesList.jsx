import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Header } from "../dashboard/leftpanel";
import { TopPanel } from "../dashboard/toppanel";

/*  List of Followees
    @TODO 
    - add notifs for likes + comments?
    - fix UIUX 
    - add pagination later for more users

    Get list of users who are followed by logged in user
   
    @author Christine Bao
*/

export function Followee_List() {
    const {username} = useParams();
    const navigate = useNavigate();
    const [followees, setFollowees] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const accessToken = localStorage.getItem("access_token");

    // fill setFollowers with follow_request NOTIF
    useEffect(() => {
        const fetchFolloweeList= async () => {
            setLoading(true);
            console.log(username)
            try {
                const response = await fetch(`http://127.0.0.1:8000/followees/${username}/`, {
                    method: "GET",
                    headers: {
                        "Authorization": `Bearer ${accessToken}`,
                        "Content-Type": "application/json", 
                    },
                });
                const data = await response.json();
                console.log(data)
                // Follow Requests retrieved successfully
                if (response.ok) {
                    setFollowees(data);
                  } else {
                    setError(data.error || "Follow Requests not found.");
                  }
            } catch (error) {
                setError("Failed to fetch follow requests. Please try again.");
            } finally {
                setLoading(false);
            }};

        fetchFolloweeList();
    }, [username])

    return(
    <div className="min-h-screen">
        {/* Top Panel (Navigation, Search, Profile) */}
        <TopPanel />
        {/* Main Layout */}
        <div className="flex mt-4">
            {/* Sidebar (Navigation, Contacts) */}
            <div className="w-1/4 border-r border-gray-300 px-4">
                <Header />
            </div>

            {/* Main Content (Follow Requests) */}
            <div className="flex flex-col w-3/4 mx-auto max-w-3xl">
                {/* Create Post at the Top */}
                <div className="mb-6">
                    <h2 className="text-2xl font-bold mb-4">Follower List</h2>
                    {loading ? (  // Loading State while Follow Request data is being fetched
                        <p className="text-blue-500"> Fetching Followers... </p>
                    ) : error ? ( // Error State if an error occurs while fetching Follow Request
                        <p className="text-red-500">{error}</p>
                    ) : followees.length === 0 ? (
                        <p>Nobody's Here Yet</p>
                    ) : (
                        <ul className="space-y-6">
                            {followees.map((followee) => (
                                <li key={followee.id} className="bg-white p-4 rounded shadows flex items-stretch">
                                    <h3 className="items-start text-xl font-semibold"
                                    >
                                        {followee.follower_username}
                                    </h3>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            </div>
        </div>
    </div>
    )
}
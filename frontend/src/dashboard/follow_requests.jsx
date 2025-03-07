import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Header } from "./leftpanel"; import { TopPanel } from "./toppanel";

/*  Notifications
    @TODO add notifs for likes + comments?
    Notification currently displays list of Follow Requests for User currently logged in.
    Each Follow Request has a button to accept or deny the request.
    Logged in User is able to click username of Follow Request sender to view their profile.
    @author Christine Bao
*/
export function Follow_Requests(){
    const navigate = useNavigate();
    const [notifs, setNotifs] = useState([]);
    const [loading, setLoading] = useState(true);
    const accessToken = localStorage.getItem("access_token");

    // fill setNotifs with follow_request NOTIF
    useEffect(() => {
        const fetchFollowRequests = async () => {
            setLoading(true);
            try {
                const response = await fetch("http://127.0.0.1:8000/notifs/follow_requests/", {
                    method: "GET",
                    headers: {
                        "Authorization": `Bearer ${accessToken}`,
                        "Content-Type": "application/json", 
                    },
                });
                const data = await response.json();
                
                // Follow Requests retrieved successfully
                if (response.ok) {
                    setNotifs(data);
                  } else {
                    setError(data.error || "Follow Requests not found.");
                  }
            } catch (error) {
                setError("Failed to fetch follow requests. Please try again.");
            } finally {
                setLoading(false);
            }};

        fetchFollowRequests();
    }, [])

    // Loading State while Follow Request data is being fetched
    if (loading) {
        return (
            <div className="flex justify-center items-center min-h-screen">
            <p>Fetching Follow Requests...</p>
            </div>        
        );
    }
    // Error State if an error occurs while fetching Follow Request
    if (error) {
        return (
          <div className="flex justify-center items-center min-h-screen">
            <p className="text-red-500">{error}</p>
          </div>
        );
    }
    // Render the Follow Reqeusts
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
                        <h2 className="text-2xl font-bold mb-4">Follow Requests</h2>
                        {notifs.length === 0 ? (<p>It's Quiet...</p>) : (
                            <ul className="space-y-6">
                                {notifs.map((notif) => (
                                    <li key={notif.id} className="bg-white p-4 rounded shadow">
                                        <h3 className="text-xl font-semibold">{notif.sender} wants to follow you!</h3>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

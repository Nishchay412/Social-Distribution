import React from "react";
import { useParams } from "react-router-dom";
import { API_BASE_URL } from "../../../config";
/*  Follow Button
    @TODO - add a hover state
    Appears if you are not following this user or have no outgoing follow request to this user
    OnClick will create a follow request to this user
    
    @author Christine Bao
*/
const Follow_Button = () => {
    const { username } = useParams();
    const accessToken = localStorage.getItem("access_token");
    
    //Follow User
    const createFollowRequest = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/profile/${username}/follow-request/`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${accessToken}`,
                    "Content-Type": "application/json", 
                },
            });
            const data = await response.json();
            
            if (response.ok){ 
                console.log("Follow Request Sent!")      
                        
            } else {
                console.log(data)
            }
        } catch {
            console.log("Issue sending Follow Request")
        }
    };

    return(
        <button 
            className="item-start mt-4 bg-purple-500 hover:bg-purple-600 text-white py-2 px-4 rounded"
            onClick={() => createFollowRequest(username)}
        >
            FOLLOW
        </button>
    )
}

export default Follow_Button;
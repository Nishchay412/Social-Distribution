import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

/*  Pending Button
    @TODO - add a hover state
    Appears if you have sent a follow request to a user that has not denied or accepted it yet
    OnClick will cancel the follow request
    
    @author Christine Bao
*/
const Pending_Button = () => {
    const { username } = useParams();
    const accessToken = localStorage.getItem("access_token");
    
    //Cancel Follow Request
    const cancel_follow_request = async () => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/profile/${username}/cancel-follow-request/`, {
                method: "DELETE",
                headers: {
                    "Authorization": `Bearer ${accessToken}`,
                    "Content-Type": "application/json", 
                },
            });
            const data = await response.json();
            console.log(data)
            
            if (response.ok){ 
                console.log("Unfollowed User!")      
                        
            } else {
                console.log(data)
            }
        } catch {
           console.log("Issue Unfollowing User")
        }
    };

    return(
        <button 
            className="item-start mt-4 bg-purple-500 hover:bg-purple-600 text-white py-2 px-4 rounded"
            onClick={() => cancel_follow_request(username)}
        >
            PENDING
        </button>
    )
}

export default Pending_Button;
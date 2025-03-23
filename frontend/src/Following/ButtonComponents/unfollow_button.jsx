import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { API_BASE_URL } from "../../../config";

/*  Unfollow Button
    @TODO - add a hover state
    Appears if you are already following the user
    OnClick will unfollow.remove this user from your following
    
    @author Christine Bao
*/
const Unfollow_Button = () => {
    const { username } = useParams();

    const accessToken = localStorage.getItem("access_token");
    
    //Unfollow User
    const createFollowRequest = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/profile/${username}/unfollow/`, {
                method: "DELETE",
                headers: {
                    "Authorization": `Bearer ${accessToken}`,
                    "Content-Type": "application/json", 
                },
            });
            const data = await response.json();
            
            if (response.ok){ 
                console.log("Unfollowed User!");          
            } else {
                console.log(data);
            }
        } catch{
            console.log("Issue Unfollowing User");
        }
    };


    return(
        <button 
            className="item-start mt-4 bg-purple-500 hover:bg-purple-600 text-white py-2 px-4 rounded"
            onClick={() => createFollowRequest(username)}
        >
            UNFOLLOW
        </button>
    )
}

export default Unfollow_Button;
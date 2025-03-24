import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Follow_Button from "./ButtonComponents/follow_button";
import Unfollow_Button from "./ButtonComponents/unfollow_button";
import Pending_Button from "./ButtonComponents/pending_button";
import { API_BASE_URL } from "../../config";
/*  Profile Button
    @TODO 
    - Page has to be refreshed to show Button
    - Edit Button Functionlity (add if we combine profiles of ones own profile and another user's profile)
    - Add 'get_relationship' call to Profile rather than Folllow Button

    Profile Button will show appropriate text depending on the relationship between 
    the User whose profile is being visited and the User who is logged in.
    Profile Button text will display:
        'FOLLOW' for users we do not follow.
        'UNFOLLOW' for users we do follow and are friends with
        'PENDING' for users we have outstanding follow_requests for

    @author Christine Bao
*/

const Relation_Button = () => {
    const { username } = useParams();
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);
    const [buttonText, setButtonText] = useState("FOLLOW");
    const accessToken = localStorage.getItem("access_token");

    //Fetch Relationship between Logged-in User and User from Profile
    useEffect(() => {
        const fetchRelationship = async () => {
            setLoading(true);
            try {
                const response = await fetch(`${API_BASE_URL}/${username}/relationship`, {
                    method: "GET",
                    headers: {
                        "Authorization": `Bearer ${accessToken}`,
                        "Content-Type": "application/json", 
                    },
                });
                const data = await response.json();
                console.log(data)
                if (response.ok){
                    if (data['relation'] =="YOURSELF"){
                        changeButtonText("EDIT");
                    } else if (data['relation'] == "FRIEND" || data['relation'] == "FOLLOWEE"){
                        changeButtonText("UNFOLLOW");
                    } else if (data['relation'] == "PENDING"){
                        changeButtonText("PENDING")
                    }else{
                        changeButtonText("FOLLOW")
                    };  
                             
                } else {
                    console.log(data)
                    setError(data.error || "Issue retrieving User Relationship")
                }
            } catch (error){
                setError("Issue retrieving User Relationship")
            } finally {
                setLoading(false);
            }
        };
        fetchRelationship();
    }, [username]);

    //Change Button Text
    const changeButtonText = (text) => {
        setButtonText(text)
    }

    return (
        <div className = "w-full h-fit content-start flex items-stretch">
            {loading ? (
                <p>...</p>
            ) : error ? (
                <p className="text-red-500">{error}</p>
            ) : buttonText === "PENDING" ? (
                <Pending_Button/>       
            ): buttonText === "UNFOLLOW" ? (
                <Unfollow_Button/>
            ) : (
                <Follow_Button/>
            )}
        </div>
    )
};

export default Relation_Button;
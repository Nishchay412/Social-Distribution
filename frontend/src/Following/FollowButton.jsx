import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

/*  Follow Button
    @TODO 
    - Button has a slight delay in showing up
    - Edit Button Functionlity (add if we combine profiles of ones own profile and another user's profile)
    
    Follow Button will show appropriate text depending on the relationship between 
    the User whose profile is being visited and the User who is logged in.
    @author Christine Bao
*/

const Follow_Button = () => {
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
                const response = await fetch(`http://127.0.0.1:8000/${username}/relationship`, {
                    method: "GET",
                    headers: {
                        "Authorization": `Bearer ${accessToken}`,
                        "Content-Type": "application/json", 
                    },
                });
                const data = await response.json();
                
                if (response.ok){
                    if (data['relation'] =="YOURSELF"){
                        changeButtonText("EDIT")
                    } else if (data['relation'] == "FRIEND" || data['relation'] == "FOLLOWEE"){
                        changeButtonText("UNFOLLOW")
                    } else if (data['relation'] == "PENDING"){
                        changeButtonText("PENDING")
                    }else{
                        changeButtonText("FOLLOW")
                    };  
                             
                } else {
                    console.log("data")
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

    const changeButtonText = (text) => {
        setButtonText(text)
    }

    return (
        <div className = "w-full h-fit content-start flex items-stretch">
            {loading ? (<p></p>) : error ? (<p className="text-red-500">{error}</p>
            ) : (
            <button className="item-start mt-4 bg-purple-500 hover:bg-purple-600 text-white py-2 px-4 rounded">
                {buttonText}
            </button>
            )}
        </div>

    )
};

export default Follow_Button;
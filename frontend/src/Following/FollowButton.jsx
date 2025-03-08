import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

/*  Follow Button
    @TODO 
    - combine user profile and friends profile to one (?)
    - add onClick functions to buttons
   
    @author Christine Bao
*/

const Follow_Button = () => {
    const { username } = useParams();
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);
    const button_text = 'FOLLOW';
    const accessToken = localStorage.getItem("access_token");


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
                console.log("fart", data);
                if (response.ok){
                    if (data.response == 'YOURSELF'){
                        button_text  = 'YOURSELF';
                    } else if (data.response == 'FRIEND' || data.response == 'FOLLOWEE'){
                        button_text = 'UNFOLLOW';
                    } else if (data.response == 'PENDING'){
                        button_text = 'PENDING';
                    };               
                } else {
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

    return (
        <div className = "w-full h-fit content-start flex items-stretch">
            <button className="item-start mt-4 bg-purple-500 hover:bg-purple-600 text-white py-2 px-4 rounded">
                {button_text}
            </button>
        </div>

    )
};

export default Follow_Button;
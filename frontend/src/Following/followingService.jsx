import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

/*  Following Services
    @TODO 
    - add description

*/

/*  Click Follow Button
    @TODO 
    - create 
    - create follow requests or unfollow users
     @author Christine Bao
*/
export default function Click_Follow_Button(text) {   
    if (text == 'FOLLOW'){
        console.log(`Hello, world! ${text}`);

    }else if (text == 'UNFOLLOW'){
        try{
            const response = fetch(`http://127.0.0.1:8000/${username}/unfollow`, {
                method: "DELETE",
                headers: {
                    "Authorization": `Bearer ${accessToken}`,
                    "Content-Type": "application/json", 
                    },
            });
            const data = response.json();
            console.log('fart: ', data);
            if (response.ok){
                console.log(data)
            } else {
                console.log(data)
            }
        } catch{
            console.log("Error Occured")
        }
    }

}
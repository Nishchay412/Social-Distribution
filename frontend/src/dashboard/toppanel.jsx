import React from "react";

import { API_BASE_URL } from "../../config";
export function TopPanel(){
    const profilepic = localStorage.getItem("profilepic")
    const first_name = localStorage.getItem("firstname")
    return(
        <div className="flex justify-between">
            <h1 className="font-sans text-gray-400">
                Verdigris
            </h1>
            <div className="flex gap-2">
                <h1 className="font-semibold py-2">
                    {first_name}
                </h1>
            <img src={profilepic} className="w-12 h-12 rounded-4xl">
                </img>
            </div>
            
        </div>
    )
}
import ImageContainer from '../imageContainer.tsx'
import { get_Stations } from "../lib/get_Stations"
import Db_UserContents from "./db_component"
import Sidebar from './sidebar'
import FilesModelsCard from './files-and-models'
import JobQueueCard from './job_queue'
import ProjectsJoined from './projects-joined'
import AnnImg_detailed from './annImg-detailed-view'

import React from "react";
import { auth } from "@/app/lib/auth";


export default async function DashLayout({children}){
    const stationdata = await get_Stations();
    const session = await auth();

    return(
        <div className="pt-5 pb-8 z-0">
            <ImageContainer stations={stationdata.features} session={session}/>
            {!session?.user ? <p>Not logged in</p>
            :
            <>
                {children}
            </>
            }
        </div>

    )

}
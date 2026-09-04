import ImageContainer from '../imageContainer.tsx'
import { get_Stations } from "../lib/get_Stations"
import { auth } from "@/app/lib/auth";
import Db_UserContents from "./db_component"


export default async function Dashboard(){
    const stationdata = await get_Stations();
    const session = await auth();


    return(
        <div className="pt-5 pb-8 z-0">
            <ImageContainer stations={stationdata.features} session={session}/>
            {!session?.user ? <p>Not logged in</p>
            :
            <Db_UserContents session={session}/>
            }
        </div>
    );
};
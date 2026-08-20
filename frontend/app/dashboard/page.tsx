import ImageContainer from '../imageContainer.tsx'
import { get_Stations } from "../lib/get_Stations"
import { auth } from "@/app/lib/auth";


export default async function Dashboard(){
    const stationdata = await get_Stations();
    const session = await auth();
    console.log("SESSION ", session)
     if (!session?.user) {
    return <p>Not logged in</p>;
  }


    return(
        <div className="pt-5 pb-8 z-0">
            <ImageContainer stations={stationdata.features} session={session}/>
            <div className="mt-8">
                <p>dashboard</p>
                 <p>Username: {session?.user?.username}</p>
                 <p>Email: {session?.user?.email}</p>
            </div>
        </div>
    );
};
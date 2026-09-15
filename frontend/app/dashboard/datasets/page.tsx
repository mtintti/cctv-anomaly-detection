import { auth } from "@/app/lib/auth";
import DatasetMain from "./datasets-component"
export default async function Datasets(){
    const session = await auth();

    return(
        <DatasetMain session={session}/>
    )
}
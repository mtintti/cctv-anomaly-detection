import { auth } from "@/app/lib/auth";

export async function GET(request:NextRequest){
    const session = await auth()
    console.log("getting GET request session..", session);
    const get_postgres_response = await fetch(`http://localhost:8000/auth/get_postgres_training_recents/${session.user.email}`, {cache: 'no-store'})

    if(!get_postgres_response.ok){
        console.log("status was not found ",get_postgres_response.status)
        console.log("typeof ", typeof(get_postgres_response))

        return Response.json({status: get_postgres_response.status});

    } else if(get_postgres_response.ok){
        //const predictiondata = await prediction_response
        const db_data = await get_postgres_response.json();
        //console.log("db_data", db_data)
        return Response.json(db_data);
    }
}
import { auth } from "@/app/lib/auth";

export async function POST(request:NextRequest){
    const session = await auth()
    console.log("getting GET request session..", session);
    if (!session?.user?.email) {
        return Response.json(
            { error: "Unauthorized" },
            { status: 401 }
        );
    }
    let database_content = await request.json();
    let dataset_name = request.headers.get('dataset_name')
    console.log("in route db to send", dataset_name)
    const post_sendtodb_response = await fetch(`http://localhost:8000/auth/send_to_user_dataset`,{
        method: 'POST',
        headers:{'session_email': session.user.email, 'dataset_name':dataset_name}, cache: 'no-store',
        body: JSON.stringify(database_content),}
    )

    if(!post_sendtodb_response.ok){
        console.log("status was not found ",post_sendtodb_response.status)
        console.log("typeof ", typeof(post_sendtodb_response))

        return Response.json({status: post_sendtodb_response.status});

    } else if(post_sendtodb_response.ok){
        //const predictiondata = await prediction_response
        const db_data = await post_sendtodb_response.json();
        console.log("db_data", db_data)
        return Response.json(db_data);
    }
}
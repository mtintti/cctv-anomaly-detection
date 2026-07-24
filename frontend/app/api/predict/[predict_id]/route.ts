'use server'
import { headers, cookies } from 'next/headers'
import type { NextRequest } from 'next/server'

export async function POST(request: Request,  {params}:{params:Promise<{predict_id : string}> }){
    const {predict_id} = await params
    const predicted_img_bytes_response = await fetch(`http://localhost:8000/predict/${predict_id}`,{
            method: 'POST',
            body: formData,
            cache: 'no-store',
        })

            const predicted_img_bytes = await predicted_img_bytes_response.json();
            return Response.json(predicted_img_bytes)
}

export async function GET(request:NextRequest, {params}:{predict_id : string}){
    console.log("getting GET request..");
    const {predict_id} = await params
    console.log("getting GET request..", predict_id);
    console.log("getting task_id_by_manager..");

    const cookieStore = await cookies();

    const task_idAll = cookieStore.get("task_id");
    const task_id_by_manager = task_idAll.value;
    console.log("task_id in GET", task_id_by_manager)
    const prediction_response = await fetch(`http://localhost:8000/predict/${predict_id}/${task_id_by_manager}`, {cache: 'no-store'})
    //const header_listed = await headers();
    //console.log("NextRequest headers from GET", header_listed)
    if(!prediction_response.ok){
        console.log("status was too early ",prediction_response.status)
        console.log("typeof ", typeof(prediction_response))
        return Response.json(prediction_response);
    } else if(prediction_response.ok){
        const predictiondata = await prediction_response.json();
        console.log("prediction GET api res ", predictiondata)
        return Response.json(predictiondata);
    }
}
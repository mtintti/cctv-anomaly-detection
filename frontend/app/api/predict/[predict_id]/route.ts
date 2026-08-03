'use server'
import { headers, cookies } from 'next/headers'
import type { NextRequest } from 'next/server'
import React, {useContext } from "react";
import {Context} from '../../../providers/tanstack'


export async function RedisURLs({predictionCardData}, i,predict_id){

        console.log("RedisURLs index in ", i)
        const original_redisURL = predictionCardData[i].jsonresponse[0].original_img
        const bbox_redisURL = predictionCardData[i].jsonresponse[0].prediction[0].imageBbox
        const seg_redisURL = predictionCardData[i].jsonresponse[0].prediction[0].imageSeg
        const formData = new FormData();
        formData.append("redisURL", original_redisURL)
        formData.append("redisURL", bbox_redisURL)
        formData.append("redisURL", seg_redisURL)
        console.log("tanstack data to URL", typeof(original_redisURL), typeof(bbox_redisURL), typeof(seg_redisURL))
        //console.log("length of formData ", Object.keys(formData).length);
        console.log("predict_id to send to POST", predict_id)

        const RedisURLsPost = await POST(formData, predict_id)
        predictionCardData[i].jsonresponse[0].original_img = RedisURLsPost[0]
        predictionCardData[i].jsonresponse[0].prediction[0].imageBbox = RedisURLsPost[1]
        predictionCardData[i].jsonresponse[0].prediction[0].imageSeg = RedisURLsPost[2]
        console.log("GET images, ", typeof(predictionCardData[0].jsonresponse[0].original_img), typeof(predictionCardData[0].jsonresponse[0].prediction[0].imageBbox), typeof(predictionCardData[0].jsonresponse[0].prediction[0].imageSegmask))
        return predictionCardData


}


export async function POST(formData, predict_id){  //request: Request,  {params}:{params:Promise<{predict_id : string}> }
   // const {predict_id} = await params
   console.log("POST predict_id was gotten ", predict_id)
    const predicted_img_bytes_response = await fetch(`http://localhost:8000/predict/${predict_id}`,{
            method: 'POST',
            body: formData,
            cache: 'no-store',
        })

            const predicted_img_bytes = await predicted_img_bytes_response.json();
            return predicted_img_bytes;
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

    if(!prediction_response.ok){
        console.log("status was not found ",prediction_response.status)
        console.log("typeof ", typeof(prediction_response))

        return Response.json({status: prediction_response.status});

    } else if(prediction_response.ok){
        //const predictiondata = await prediction_response;
        console.log("prediction GET api res ", prediction_response)

        if(prediction_response.status === 200){
            const predictiondata_full = await prediction_response.json();
            let data_to_see = null;
            //const predictionCardData = predictiondata_full['found']
            //console.log("id was found, found json and record_id", predictiondata_full['found'], predictiondata_full['record by id of task'])
            const predictionCardData = JSON.parse(predictiondata_full['found'])
            console.log("fake data ", predictionCardData.length)
            for (let i = 0; i < predictionCardData.length; i++){
                console.log("in loop of RedisURLs")
                data_to_see = await RedisURLs({predictionCardData},i, predict_id)

            }

            console.log("data to see routes side ", data_to_see)
            return Response.json(data_to_see);

        }else if(prediction_response.status === 201){
            const predictiondata_processing = await prediction_response.json();
            console.log("id was not there, but record_id was", predictiondata_processing['record by id of task'])
            console.log('trying again..')
            return Response.json(predictiondata_processing, {
              status: prediction_response.status,
              headers: {
                "Retry-After":
                  prediction_response.headers.get("Retry-After") ?? "",
              },
            });

        }else if(prediction_response.status === 206){
            const predictiondata_partical = await prediction_response.json();
            console.log("parital content", predictiondata_partical)
            return Response.json(predictiondata_partical, {
              status: prediction_response.status,

            })
        }
    }
}
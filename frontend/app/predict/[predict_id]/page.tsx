
import React from 'react';
import ImageContainer from '../../imageContainer'
import ImageSearch from '../../cctvImageSearch'
import PredictionComponent from "./predictionComponent"

interface StationsRes {
  features: Station[];
}

export default async function PredictionPage({
  params,
}: {
  params: Promise<{ predict_id: string }>
}) {

    const stationsAll = await fetch("http://localhost:8000/stations", {cache: 'force-cache'});
    const stationdata: StationsRes = await stationsAll.json();
    const {predict_id} = await params;
    console.log("params are, ", params, " and id as ", predict_id)
    const image = {
        image_base_origScr: null,
        image_bbox_Scr: null,
        image_seg_Scr: null
    };

    var object_prediction_data = null


    const prediction_response = await fetch(`http://localhost:8000/predict/${predict_id}`, {cache: 'no-store'})
    const predictiondata = await prediction_response.json();
    console.log("gotten predictiondata ,", predictiondata)
    console.log("type ", typeof(predictiondata))
    if (typeof predictiondata == 'string'){
        object_prediction_data = JSON.parse(predictiondata)
        console.log(typeof(object_prediction_data))
        console.log("object prediction to pass, ", object_prediction_data)

        const original_redisURL = object_prediction_data[0].jsonresponse[0].original_img
        console.log("segment and bbox? ",object_prediction_data[0].jsonresponse[0].prediction[0].imageBbox)
        const bbox_redisURL = object_prediction_data[0].jsonresponse[0].prediction[0].imageBbox
        const seg_redisURL = object_prediction_data[0].jsonresponse[0].prediction[0].imageSeg
        const formData = new FormData();
        formData.append("redisURL", original_redisURL)
        formData.append("redisURL", bbox_redisURL)
        formData.append("redisURL", seg_redisURL)


        const predicted_img_bytes_response = await fetch(`http://localhost:8000/predict/${predict_id}`,{
            method: 'POST',
            body: formData,
            cache: 'no-store',
        })


            const predicted_img_bytes = await predicted_img_bytes_response.json();
            if (typeof predicted_img_bytes == 'string'){
                console.log("type of predicted_img_bytes is ?? ",typeof(predicted_img_bytes))
                const object_predicted_img_bytes = JSON.parse(predicted_img_bytes)
                console.log("bytes received ", typeof(object_predicted_img_bytes))
            } else if (typeof predicted_img_bytes == 'object'){
                image.image_base_origScr = predicted_img_bytes[0]
                image.image_bbox_Scr = predicted_img_bytes[1]
                image.image_seg_Scr = predicted_img_bytes[2]
                console.log("GET images, ", typeof(image_base_origScr), typeof(image_bbox_Scr), typeof(image_seg_Scr))

            }


    } else if (typeof predictiondata == 'object'){
        console.log(predictiondata)
    }


     return(
        <div className="pt-5 pb-4 z-0">
            <ImageContainer stations={stationdata.features}/>
            <PredictionComponent images={image} jsonmeta={object_prediction_data}/>
        </div>
     )
}
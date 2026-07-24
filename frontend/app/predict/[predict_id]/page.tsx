'use server'
import React from 'react';
import ImageContainer from '../../imageContainer'
import ImageSearch from '../../cctvImageSearch'
import PredictionMain from "./PredictionMain"
import { get_Stations } from "../../lib/get_Stations"


export default async function PredictionPage({
  params,
}: {
  params: Promise<{ predict_id: string }>
}) {

    //const stationsAll = await fetch("http://localhost:8000/stations", {cache: 'force-cache'});
    const stationdata = await get_Stations();
    const {predict_id} = await params;



    {/*const prediction_response = await fetch(`http://localhost:8000/predict/${predict_id}`, {cache: 'no-store'})
    if(!prediction_response.ok){
        console.log("status was too early ",prediction_response.status)
        console.log("typeof ", typeof(prediction_response))
    } else if(prediction_response.ok){
    const predictiondata = await prediction_response.json();
    //console.log("type ", typeof(predictiondata))
    if (typeof predictiondata == 'string'){
        predictionCardData = JSON.parse(predictiondata)

        // predictionCardData sisältää lähetettyjen kuvien ja tiedoston 'jsonmeta' tiedot, ja pituus on N pitkä perustuen json_response_all pituuteen.object_prediction_data
        // predictionCardData loopataan .map() käyttämällä predictionComponent:in sisällä näyttäen N pituuta key={N}. curr.jsonresponse[0].details[0].class_name on 1.json[0]...class_name, 2.json[0]...class_name ja niin edelleen
        // 1.class_name, 2.class_name ja 3.class_name käytetään GET requestin pruunaamiseen, predictionCardData[0] on [0]class_name
        // Nämä loopataan kaikkien predictiondata N pituuden ja tehdään GET request jokaisesta saadusta 3 redisURL stringistä jotta saamme kaikki mahdolliset kuvan kuvat kerralla frontend predictionComponent:iin
        // näin voimme näyttää class_name nimeä klikkaamalla löydön front-end:issä ilman turhia, ja 'jälkeenpäin' reaali-aikaisia tehtyjä GET requesteja klikkaus hetkellä
        for (let i = 0; i < predictionCardData.length; i++){
        const original_redisURL = predictionCardData[i].jsonresponse[0].original_img
        const bbox_redisURL = predictionCardData[i].jsonresponse[0].prediction[0].imageBbox
        const seg_redisURL = predictionCardData[i].jsonresponse[0].prediction[0].imageSeg
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
                const object_predicted_img_bytes = JSON.parse(predicted_img_bytes)
            } else if (typeof predicted_img_bytes == 'object'){
                predictionCardData[i].jsonresponse[0].original_img = predicted_img_bytes[0]
                predictionCardData[i].jsonresponse[0].prediction[0].imageBbox = predicted_img_bytes[1]
                predictionCardData[i].jsonresponse[0].prediction[0].imageSeg = predicted_img_bytes[2]
                console.log("GET images, ", typeof(predictionCardData[0].jsonresponse[0].original_img), typeof(predictionCardData[0].jsonresponse[0].prediction[0].imageBbox), typeof(predictionCardData[0].jsonresponse[0].prediction[0].imageSegmask))
            }
        }
    }

    // none found : predict_id,
    } else if (typeof predictiondata == 'object'){
        predictionCardData = Fallback_ui
        console.log("fallback_ui data is")
        console.log(typeof(Fallback_ui), " and contains")
        console.log(Fallback_ui)
        console.log(predictionCardData)

    }*/}




     return(
        <div className="pt-5 pb-4 z-0">
            <ImageContainer stations={stationdata.features}/>
            {/*<PredictionComponent predictionCardData={predictionCardData}/>*/} {/*images={image} jsonmeta={object_prediction_data}*/}
                <div className="pt-2 justify-center py-2 px-2">
                    <PredictionMain predict_id={predict_id}/>
            </div>
        </div>
     )
}
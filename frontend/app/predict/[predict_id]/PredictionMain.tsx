'use client'
import Image from 'next/image';
import { Suspense, useState } from 'react';
import predictedImage from "../../../public/prediction-v9.jpg"
import { Fallback_ui } from './lib/fallback_ui'


// sama structuuri kuin ml/schema/ json_response
interface Predictiondetails {
  class_id: number;
  class_name: string;
  confidence_score: number;
}

interface Inviprediction {
  imageBbox: string;
  imageSeg: string;
}

interface Jsonresponse {
  belongsto: string;
  original_img: string;
  img_w: number;
  img_h: number;
  details: Predictiondetails[];
  prediction: Inviprediction[];
}

interface PredictionEntry {
  predict_id: string;
  jsonresponse: Jsonresponse[];
}

let predictionCardData: PredictionEntry[] = Fallback_ui;


//export default async function PredictionMain({predictionCardData}:{predictionCardData: object}){
export default function PredictionMain({predict_id}:{predict_id: string}){

    try{
        const predictionCardData = fetch(`/api/predict/${predict_id}`);
        console.log("if success ", predictionCardData)
    } catch (error){
        console.log("error, ", error);
    }

    const [clicked_index, setClicked_index] = useState(0);
    //let img_w = predictionCardData[0].jsonresponse[0].img_w
    //let img_h = predictionCardData[0].jsonresponse[0].img_h
    console.log("clicked_index is ,", clicked_index)


return(
    <div className="bg-gray-100 md:py-3 md:px-3 inset-shadow-sm inset-shadow-gray-300 grid md:grid-cols-2">
                        <div className="">
                            <div className={`relative w-[360px] md:w-[700px] md:h-[400px] lg:w-[800px] h-[340px] shadow-xl shadow-gray-200`}>
                                 {predictionCardData[clicked_index].jsonresponse[0].prediction[0].imageBbox != null ?<>
                                     <img className="absolute w-full h-full" src={predictionCardData[clicked_index].jsonresponse[0].original_img}/>
                                     <img className="absolute w-full h-full" src={predictionCardData[clicked_index].jsonresponse[0].prediction[0].imageBbox}/>
                                    <img className="absolute w-full h-full" src={predictionCardData[clicked_index].jsonresponse[0].prediction[0].imageSeg}/>
                                    </>
                                 :
                                  <>
                                     <img className="absolute w-full h-full " src={predictionCardData[clicked_index].jsonresponse[0].original_img}/>
                                  </>
                                }
                            </div>

                        </div>
                        <div className="col-span-2  md:col-span-2 bg-gray-300">
                            <div className="justify-center">
                                {predictionCardData.map((curr, i) => (
                                    <div key={i}
                                     onClick={() => setClicked_index(i)}
                                     className={`relative pr-1 flex ${i==clicked_index ? 'bg-gray-200' :'bg-slate-400'} h-full inline-block font-extralight px-2 pt-1 mt-3`}>
                                        {predictionCardData[i].jsonresponse[0].details[0].class_name}
                                    </div>
                                ))}
                                <div className="w-[360px] md:w-[700px] lg:w-[800px] font-normal bg-gray-200">
                                    <div className="pl-10 pt-4 pr-10 grid grid-rows-1 tracking-tight font-bold">
                                    <p className="pb-2 text-xl font-medium">{predictionCardData[clicked_index].jsonresponse[0].belongsto}</p>
                                    <div className="grid row-start-2 pt-2">
                                        <p className="font-light text-md pb-2">confidence_score of model</p>
                                        <p className="font-light text-md">class_id of model</p>
                                        </div>
                                         <div className="grid pr-10 row-start-2">
                                            <p className="pb-2">{predictionCardData[clicked_index].jsonresponse[0].details[0].confidence_score}</p>
                                            <p>{predictionCardData[clicked_index].jsonresponse[0].details[0].class_id}</p>
                                        </div>
                                    </div>

                                </div>
                            </div>
                        </div>
                    </div>

    )
}

/* <span className="text-large font-light">
                    <div className="col-span-1 md:grid-cols-3 gap-2 my-2">
                        <div className="inline-block bg-teal-300 text-teal-800 pl-2 py-1 rounded-full">
                            <p className="text-sm font-light">Traverse Crack</p>
                        </div>
                        <div className="inline-block bg-cyan-500 text-cyan-800 pl-2 py-1 rounded-full">
                            <p className="text-sm font-light">Longitudinal crack</p>
                        </div>
                        <div className="inline-block bg-blue-950 text-blue-300 pl-2 py-1 rounded-full">
                            <p className="text-sm font-light">Other corruption</p>
                        </div>
                    </div>
                </span> */
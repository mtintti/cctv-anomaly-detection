'use client'
import Image from 'next/image';
import { Suspense, useState } from 'react';
import predictedImage from "../../../public/prediction-v9.jpg"
import { Fallback_ui } from './lib/fallback_ui'

import {
  useQuery,
  useMutation,
  useQueryClient,
  QueryClient,
  QueryClientProvider,
} from '@tanstack/react-query'


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



//export default async function PredictionMain({predictionCardData}:{predictionCardData: object}){
export default function PredictionMain({predict_id}:{predict_id: string}){
    const [refetch_time, setRefetch_time] = useState(5000)

    {/*try{
        const predictionCardData = fetch(`/api/predict/${predict_id}`);
        console.log("if success ", predictionCardData)
    } catch (error){
        console.log("error, ", error);
    }*/}
    //var refetch_time = null
    const queryClient = useQueryClient()
    const { isPending, error, data, isFetching } = useQuery({ queryKey: ['preds'],
        queryFn: async () => {
        const res = await fetch(`/api/predict/${predict_id}`,)
        //console.log("res query headers", res.headers.entries() )//get('Retry-After'))
        for (const [key, value] of res.headers.entries()) {
          console.log(`${key}: ${value}`);
        }
        console.log("res status set in backend ",res.status)
        console.log("refetch_time set ... ", refetch_time)
        console.log(typeof(Number(res.headers.get('Retry-After'))))
        setRefetch_time(Number(res.headers.get('Retry-After')))
        console.log("refetch_time set now?? ",refetch_time )

        return await res.json()
        },
        refetchInterval: refetch_time,

    });
        console.log("refetch_time set now global?? ",refetch_time)


    if(data != undefined){
        console.log("res in tanstack ", data)
        console.log(typeof(data))
        console.log("was it true, ", data['found'])
        if(typeof(data['found']) === 'string'){
            console.log("was it true, ", data['found'])
            var data_to_show = JSON.parse(data['found'])
            console.log("data JSON.parsed")

        }

    }

let predictionCardData: PredictionEntry[] = data ?? Fallback_ui;


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

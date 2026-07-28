'use client'
import React, { useState, useContext, useEffect } from "react";
import Image from 'next/image';
import {Context} from '../../providers/tanstack'
import { Fallback_ui } from './lib/fallback_ui'
import ErrorModal from './error-modal'
import Skeleton from './skeleton'


import {
  useQuery,
  useMutation,
  useQueryClient,
  QueryClient,
  QueryClientProvider,
  useIsFetching
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


export default function PredictionMain({predict_id}:{predict_id: string}){
    const [refetch_time, setRefetch_time] = useState(1000);
    const [errormodalMessage, seterrormodalMessage] = useState(null);
    const [skeletonMessage, setSkeletonMessage] = useState(null);
    const {errormodelSeeable,setErrormodelSeeable, pending, setPending} = useContext(Context);
    const [clicked_index, setClicked_index] = useState(0);
    const isFetching_toshow = useIsFetching();


    const queryClient = useQueryClient()
    const { isPending, error, data, isFetching } = useQuery({ queryKey: ['preds'],
        queryFn: async () => {
        const res = await fetch(`/api/predict/${predict_id}`,)
        for (const [key, value] of res.headers.entries()) {
          console.log(`${key}: ${value}`);
        }
        console.log("res status set in backend to front ",res.status)
        console.log("refetch_time set ... ", refetch_time)
        console.log(typeof(Number(res.headers.get('Retry-After'))))
        setRefetch_time(Number(res.headers.get('Retry-After')))
        console.log("refetch_time set now?? ",refetch_time )

        return await res.json()
        },
        refetchInterval: refetch_time,

    });


useEffect(() => {
    if (!data) return;
    console.log("data from tanstack ", data)

    if (data.status === 404) {
        setErrormodelSeeable(true);
        seterrormodalMessage("404");
        setSkeletonMessage(null)
        setPending(false)
        return;
    }

    if (data["record by id of task"]) {
        if(data["record by id of task"].status === 'success'){
            setErrormodelSeeable(true);
            seterrormodalMessage(data["record by id of task"].status);
            setSkeletonMessage(null)
            setPending(false)
            console.log("errormodalMessage ", errormodalMessage)
        } else {
            setErrormodelSeeable(false);
            setSkeletonMessage(data["record by id of task"].status);
        }
    }


    if (Array.isArray(data)) {
        setErrormodelSeeable(false);
        setPending(false)
        setSkeletonMessage(null)
        return;
    }
}, [data]);

const predictionCardData: PredictionEntry[]  =
    Array.isArray(data) ? data : Fallback_ui;



return(
    <>
    {pending === true || skeletonMessage != null || isPending === true ? <Skeleton skeletonMessage={skeletonMessage} clicked_index_passed={clicked_index}/>
        :

    <div className="bg-gray-100 md:py-3 md:px-3 inset-shadow-sm inset-shadow-gray-300 grid md:grid-cols-2">
                        <div>
                            <div className={`relative min-w-[360px] md:h-[400px] max-w-[800px] lg:w-[800px] h-[340px] shadow-xl shadow-gray-200`}>
                            <div> { errormodelSeeable === true && <ErrorModal errormodalMessage={errormodalMessage}/> }</div>
                            {errormodelSeeable === false && <div>
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
                                <div className="min-w-[360px] max-w-[800px] font-normal bg-gray-200">
                                    <div className="pl-10 pt-4 pr-10 grid grid-rows-1 tracking-tight font-bold">
                                    <p className="pb-2 text-base font-sm md:text-xl md:font-medium">{predictionCardData[clicked_index].jsonresponse[0].belongsto}</p>
                                    <div className="grid row-start-2 pt-2">
                                        <p className="font-light text-md pb-2">confidence score of model</p>
                                        <p className="font-light text-md">class id of model</p>
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
                    }
                </>

    )
}

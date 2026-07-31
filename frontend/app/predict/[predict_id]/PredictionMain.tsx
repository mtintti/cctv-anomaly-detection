'use client'
import React, { useState, useContext, useEffect } from "react";
import Image from 'next/image';
import {Context} from '../../providers/tanstack'
import { Fallback_ui } from './lib/fallback_ui'
import ErrorModal from './error-modal'
import Skeleton from './skeleton'
import graph from '../../../public/3dicons-graph.png'


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

interface Metrics {
    handling: string;
    preprocess_to_tensor: string;
    inference: string;
    bbox_and_segmask: string;
    original_img_encode: string;
    batchlist: string;
    encode_img_tag: string;
    redis: string;
    whole_runs_time: string;
}


interface PredictionEntry {
  predict_id: string;
  jsonresponse: Jsonresponse[];
  metrics: Metrics[];
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
        console.log("prediction json was ", data[0].metrics.handling)
        return;
    }
}, [data]);

const predictionCardData: PredictionEntry[]  =
    Array.isArray(data) ? data : Fallback_ui;

console.log("pic data ", predictionCardData[clicked_index].jsonresponse[0].original_img)


return(
    <>
    {pending === true || skeletonMessage != null || isPending === true ? <Skeleton skeletonMessage={skeletonMessage} clicked_index_passed={clicked_index}/>
        :

    <div className="bg-gray-100 min-w-[360px] md:py-3 md:px-3 inset-shadow-sm inset-shadow-gray-300">
                        <div className="grid md:grid-cols-3 flex pb-4">
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
                        {/* space between components */}
                        <div className="w-10 "></div>

                        <div className="bg-purple-100/70 min-w-100 max-w-200 h-full max-md:hidden items-center inset-shadow-sm inset-shadow-purple-300">
                            <div className="font-light tracking-tight text-lg text-slate-700">
                                    <div className="my-6 mx-40 h-64">
                                            <div className="h-50 pt-30 my-4 mx-4 text-2xl">
                                                <p>{predictionCardData[0].metrics.whole_runs_time} ms</p>
                                            </div>
                                            <div className="text-center items-center justify-center mb-4">
                                                <p>Whole runs time</p>
                                                <div className="flex gap-3 pl-30 top-10">
                                                    <div className="py-2 px-2 bg-red-100 h-4 w-4 rounded-full"></div>
                                                    <div className="py-2 px-2 bg-red-100 h-4 w-4 rounded-full"></div>
                                                </div>
                                            </div>
                                    </div>
                            </div>
                        </div>
                        </div>
                        <div className="col-span-2 md:col-span-2 bg-gray-300">
                            <div className="justify-center">
                                {predictionCardData.map((curr, i) => (
                                    <div key={i}
                                     onClick={() => setClicked_index(i)}
                                     className={`relative pr-1 flex ${i==clicked_index ? 'bg-gray-200' :'bg-slate-400'} h-full inline-block font-extralight px-2 pt-1 mt-3`}>
                                        {predictionCardData[i].jsonresponse[0].details[0].class_name}
                                    </div>
                                ))}
                                <div className="min-w-[360px] max-w-[800px] font-normal bg-gray-200 pb-4">
                                    <div className="pl-10 pt-4 pr-10 grid grid-rows-1 tracking-tight font-bold">
                                    <p className="pb-2 text-base font-sm md:text-xl md:font-medium">{predictionCardData[clicked_index].jsonresponse[0].belongsto}</p>
                                    <div className="grid row-start-2 pt-2">
                                        <p className="font-light text-md pb-2">confidence score of model</p>
                                        <p className="font-light text-md">class id of model</p>
                                        </div>
                                         <div className="grid pr-10 font-medium text-lg row-start-2">
                                            <p className="pt-2">{predictionCardData[clicked_index].jsonresponse[0].details[0].confidence_score}</p>
                                            <p>{predictionCardData[clicked_index].jsonresponse[0].details[0].class_id}</p>
                                        </div>
                                    </div>
                                </div>
                                <div className="min-md:hidden font-light tracking-tight text-lg text-slate-700">
                                    <div className="my-6 mx-4 min-w-80 h-64">
                                        <div className="bg-purple-100/70 inset-shadow-sm inset-shadow-purple-300 w-full h-full rounded-md">
                                            <div className="h-50 my-4 mx-8 text-center">
                                                <p className="text-xl pt-40">{predictionCardData[0].metrics.whole_runs_time} ms</p>
                                            </div>
                                            <div className="text-center items-center justify-center mb-4">
                                                <p>Whole runs time</p>
                                                <div className="flex gap-3 pl-55 top-6">
                                                    <div className="py-2 px-2 bg-red-100 h-4 w-4 rounded-full"></div>
                                                    <div className="py-2 px-2 bg-red-100 h-4 w-4 rounded-full"></div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="min-w-80 max-w-300 h-[500px] justify-center text-base items-center grid min-sm:grid-rows-4 min-sm:grid-cols-2 max-md:grid-rows-7 max-md:grid-cols-1 pb-4 my-2 mx-2 gap-3 text-shadow-sm text-shadow-slate-300/50">
                                        <div className="bg-gray-200 inset-shadow-sm inset-shadow-gray-400/50 w-full h-full grid grid-cols-2 rounded-md">
                                            <p className="mx-2 my-4 min-sm:pt-8">file/img handling</p>
                                            <p className="mx-2 my-4 justify-self-end text-xl mr-8 min-sm:pt-8">{predictionCardData[0].metrics.handling} ms</p>
                                        </div>
                                        <div className="bg-gray-200 inset-shadow-sm inset-shadow-gray-400/50 w-full h-full grid grid-cols-2 rounded-md">
                                            <p className="mx-2 my-2 min-sm:pt-6">img preprocess to tensor</p>
                                            <p className="mx-2 my-4 justify-self-end text-xl mr-8 min-sm:pt-8">{predictionCardData[0].metrics.preprocess_to_tensor} ms</p>
                                        </div>
                                        <div className="bg-gray-200 inset-shadow-sm inset-shadow-gray-400/50 w-full h-full grid grid-cols-2 rounded-md">
                                            <p className="mx-2 my-2 min-sm:pt-6">onnx session's Inference time</p>
                                            <p className="mx-2 my-4 justify-self-end text-xl mr-8 min-sm:pt-8">{predictionCardData[0].metrics.inference} ms</p>
                                        </div>
                                        <div className="bg-gray-200 inset-shadow-sm inset-shadow-gray-400/50 w-full h-full grid grid-cols-2 rounded-md">
                                            <p className="mx-2 my-2 min-sm:pt-6">arranging bbox and segmask</p>
                                            <p className="mx-2 my-4 justify-self-end text-xl mr-8 min-sm:pt-8">{predictionCardData[0].metrics.bbox_and_segmask} ms</p>
                                        </div>
                                        <div className="bg-gray-200 inset-shadow-sm inset-shadow-gray-400/50 w-full h-full grid grid-cols-2 rounded-md">
                                            <p className="mx-2 my-4 min-sm:pt-6">original image encode</p>
                                            <p className="mx-2 my-4 justify-self-end text-xl mr-8 min-sm:pt-8">{predictionCardData[0].metrics.original_img_encode} ms</p>
                                        </div>
                                        <div className="bg-gray-200 inset-shadow-sm inset-shadow-gray-400/50 w-full h-full grid grid-cols-2 rounded-md">
                                            <p className="mx-2 my-4 min-sm:pt-8">batchlisting items</p>
                                            <p className="mx-2 my-4 justify-self-end text-xl mr-8 min-sm:pt-8">{predictionCardData[0].metrics.batchlist} ms</p>
                                        </div>
                                        <div className="bg-gray-200 inset-shadow-sm inset-shadow-gray-400/50 w-full h-full grid grid-cols-2 rounded-md">
                                            <p className="mx-2 my-2 min-sm:pt-6">encodeded to response for img</p>
                                            <p className="mx-2 my-4 justify-self-end text-xl mr-8 min-sm:pt-8">{predictionCardData[0].metrics.encode_img_tag} ms</p>
                                        </div>
                                        <div className="bg-gray-200 inset-shadow-sm inset-shadow-gray-400/50 w-full h-full grid grid-cols-2 rounded-md">
                                            <p className="mx-2 my-2 min-sm:pt-6">redis</p>
                                            <p className="mx-2 my-4 justify-self-end text-xl mr-8 min-sm:pt-8">{predictionCardData[0].metrics.redis} ms</p>
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

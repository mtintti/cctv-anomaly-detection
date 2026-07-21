import Image from 'next/image';
import { Suspense } from 'react';
import predictedImage from "../../../public/prediction-v9.jpg"

export default function PredictionComponent({images, jsonmeta}:{images: object, jsonmeta: object}){
    if (jsonmeta != null){
        console.log("jsonmetadata ,", jsonmeta[0].jsonresponse[0].details[0])
        console.log("jsonmeta type, ", typeof(jsonmeta))
        console.log(jsonmeta[0].jsonresponse[0].details[0].class_id)
        console.log(jsonmeta[0].jsonresponse[0].details[0].class_name)
        console.log(jsonmeta[0].jsonresponse[0].details[0].confidence_score)
        console.log("length of json, ", jsonmeta.length)

    }

return(
    <div className="pt-2 justify-center bg-red-50">
        {images.image_base_origScr && jsonmeta != null ?
            <div className="bg-gray-200 py-3 px-3 sm:my-3  rounded-md inset-shadow-sm inset-shadow-gray-300 grid md:grid-cols-3">
                <div className="col-span-2">
                <div className="relative w-[800px] h-[800px]">
                     <img className="absolute w-full h-full" src={images.image_base_origScr}/>
                     <img className="absolute w-full h-full" src={images.image_seg_Scr}/>
                     <img className="absolute w-full h-full" src={images.image_bbox_Scr}/>
                </div>
                </div>
                <div className="col-span-1 bg-green-100">
                    <div className="justify-center">
                    {jsonmeta.map((curr, i) => (
                        <div key={i} className="relative flex inline-block text-sm font-extralight rounded-s-lg px-1">
                            {curr.jsonresponse[0].details[0].class_name}
                        </div>
                    ))}
                    </div>

                </div>
                <span className="text-large font-light">
                    <div className="grid md:grid-cols-3 gap-2 my-2">
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
                </span>
            </div>

            :

            <div className="bg-gray-200 py-3 px-3 sm:my-3  rounded-md inset-shadow-sm inset-shadow-gray-300 grid md:grid-cols-3">
                {/* fallback when data is shown */}
                <div className="col-span-2">
                    <Image alt="image showing segment masks, bboxes and image showing found anomalities, is a placeholder for none found" preload={true} preload={true} width={800} height={800} src={predictedImage}/>
                </div>
                <div className="col-span-1 bg-green-100">
                </div>
                <span className="text-large font-light">
                    <div className="grid md:grid-cols-3 gap-2 my-2">
                        <div className="inline-block bg-teal-300 text-teal-800 pl-2 py-1 rounded-full">
                            <p className="text-sm font-light">Traverse crack</p>
                        </div>
                        <div className="inline-block bg-cyan-500 text-cyan-800 pl-2 py-1 rounded-full">
                            <p className="text-sm font-light">Longitudinal crack</p>
                        </div>
                        <div className="inline-block bg-blue-950 text-blue-300 pl-2 py-1 rounded-full">
                            <p className="text-sm font-light">Other corruption</p>
                        </div>
                    </div>
                </span>
           </div>
        }
    </div>

    )
}
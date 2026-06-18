
import React from 'react';
import Image from 'next/image';
import ImageContainer from '../imageContainer'
import ImageSearch from '../cctvImageSearch'
import predictedImage from "../../public/prediction-v9.jpg"

interface StationsRes {
  features: Station[];
}

export default async function PredictionPage(){


    const stationsAll = await fetch("http://localhost:8000/stations", {cache: 'no-store'});
    const stationdata: StationsRes = await stationsAll.json();


     return(
        <div className="pt-5 pb-4 z-0">
            <ImageContainer stations={stationdata.features}/>
            <div className="justify-center bg-red-50">
            <div className="bg-gray-200 py-3 px-3 my-8 mx-8 rounded-md inset-shadow-sm inset-shadow-gray-300 grid grid-cols-3">
            <div className="col-span-2">
              <Image alt="predicted, segmented mask image showing found anomalities" preload={true} preload={true} width={800} height={800} src={predictedImage}/>
            </div>
            <div className="col-span-1 bg-green-100">

            </div>
            <span className="text-large font-light">
                <div className="grid grid-cols-3 gap-2 my-2">
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
            </div>
        </div>
     )
}
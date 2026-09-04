'use server'
import React from 'react';
import ImageContainer from '../../imageContainer'
import ImageSearch from '../../cctvImageSearch'
import PredictionMain from "./PredictionMain"
import { get_Stations } from "../../lib/get_Stations"
import { auth } from "../../lib/auth";


export default async function PredictionPage({
  params,
}: {
  params: Promise<{ predict_id: string }>
}) {

    //const stationsAll = await fetch("http://localhost:8000/stations", {cache: 'force-cache'});
    const stationdata = await get_Stations();
    const {predict_id} = await params;
    const session = await auth();

     return(
        <div className="pt-5 z-0">
            <ImageContainer stations={stationdata.features} session={session}/>
                <div className="pt-2 justify-center">
                    <PredictionMain predict_id={predict_id} session={session}/>
            </div>
        </div>
     )
}
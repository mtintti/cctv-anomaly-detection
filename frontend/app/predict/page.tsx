
import React from 'react';
import ImageContainer from '../imageContainer'
import ImageSearch from '../cctvImageSearch'

interface StationsRes {
  features: Station[];
}

export default async function PredictionPage(){


const stationsAll = await fetch("http://localhost:8000/stations", {cache: 'no-store'});
    const stationdata: StationsRes = await stationsAll.json();


     return(
        <div type='text'>
            page for image and stats as labels stacked all nicly
            <ImageContainer stations={stationdata.features}/>

        </div>
     )
}
import FormImage from './form-component';
import ImageContainer from './imageContainer.tsx'

interface StationsRes {
  features: Station[];
}

export default async function FrontPage(){

   const responce_got = await fetch("http://localhost:8000/", {cache: 'no-store'});
   const data_from_fetch = await responce_got.json();
    const stationsAll = await fetch("http://localhost:8000/stations", {cache: 'no-store'});
    const stationdata: StationsRes = await stationsAll.json();

    return (
    <div>
      <h1>Next.js Frontend (SSR) hellorei</h1>
      <p>Backend Response:</p>
      <ImageContainer stations={stationdata.features}/>
    </div>
  );

}

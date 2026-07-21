"use client";

import { useState } from "react";
import Link from 'next/link'
import { redirect } from 'next/navigation'

import FormImage from "./form-component";
import ImageSearch from "./cctvImageSearch";

export default function ImageContainer({
  stations,
  result
}) {
  const [selectedFile, setSelectedFile] =
    useState<File | null>(null);

  const [selectedStation, setSelectedStation] =
    useState<Station | null>(null);

  const [selectedBaseId, setSelectedBaseId] = useState(null);
  const content_tosend = [];
  let wanted_imgUrl = "";

  async function submitHandler() {
    const formData = new FormData();

    if (selectedFile != null) {
        console.log("selectedFile", selectedFile);
      formData.append("file", selectedFile);
    }

    if (selectedStation != null) {
        console.log("why is station got??," , selectedStation)
        console.log("base got, ", selectedBaseId)

        if(selectedStation && selectedBaseId != null){
            console.log(selectedStation, " -> ", selectedBaseId)
            const res = await fetch(`http://localhost:8000/camera/${selectedBaseId}`);
            const camdata = await res.json();
            const camdata_arr =  Object.values(camdata.properties.presets);
            console.log("camarr, ", camdata_arr)
            console.log("current click, ", selectedStation)
            camdata_arr.forEach(function (x, i){
            if(x.id.includes(selectedStation)){
                wanted_imgUrl = x.imageUrl;
                formData.append("url", wanted_imgUrl);
                console.log("clicked url, ", wanted_imgUrl)
             }
            }
          );

        }  else {

        }

    }
    console.log("moving to form fetch content ", formData)
    console.log(".. and its length", formData.length)
    for(let i = 0; i < formData.length; i++){
        console.log(formData[i])
    }

    const res = await fetch(
      "http://localhost:8000/predict",
      {
        method: "POST",
        body: formData,
      }, {cache: 'force-store'}
    );

    const data = await res.json();

    console.log(typeof(data))

    console.log(data.predict_id)
    var predict_id = data.predict_id
    const byteSize = (str) => new Blob([str]).size;
    console.log(byteSize(data))



    if(predict_id){
        redirect(`/predict/${predict_id}`)
    }

  }

  return (
    <div className="grid grid-cols-3 pl-4 gap-4">
      <FormImage
        onFileSelect={(file) => {
          setSelectedFile(file);
          console.log("from formImage, ", file)
          console.log("in formImage's selectedFile", selectedFile)
        }}
      />
          <ImageSearch
            stations={stations}
            selectedStation={selectedStation}
            selectedBaseId={selectedBaseId}
            onBaseSelect={(baseId) => {
          setSelectedBaseId(baseId);}}

            onStationSelect={(station) => {
              setSelectedStation(station)
            }}
          />
          <button className=" pt-1 justify-center text-white text-sm font-bold bg-indigo-400 w-18 h-8 rounded-xl inset-shadow-sm inset-shadow-indigo-300 shadow-sm shadow-indigo-500" onClick={submitHandler}>
            Submit
          </button>
    </div>
  );
}
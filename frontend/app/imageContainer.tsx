"use client";

import { useState } from "react";
import Link from 'next/link'

import FormImage from "./form-component";
import ImageSearch from "./cctvImageSearch";

export default function ImageContainer({
  stations,
}) {
  const [selectedFile, setSelectedFile] =
    useState<File | null>(null);

  const [selectedStation, setSelectedStation] =
    useState<Station | null>(null);

  const [selectedBaseId, setSelectedBaseId] = useState(null);
  const [result, setResult] = useState<any>(null);
  //const [prevCam, setprevCam] = useState("");
  const content_tosend = [];
  let wanted_imgUrl = "";

  //console.log("global selectedFile", selectedFile)
  //console.log("global selectedStation", selectedStation)

  async function submitHandler() {
    const formData = new FormData();

    if (selectedFile != null) {
        console.log("selectedFile", selectedFile);
      formData.append("file", selectedFile);
      //content_tosend.push(selectedFile)
    }

    if (selectedStation != null) {
        console.log("why is station got??," , selectedStation)
        console.log("base got, ", selectedBaseId)
        //sessionStorage.setItem("prevCam", {selectedStation: selectedStation});
        //let prevCam = sessionStorage.getItem("prevCam")
        //prevCam = selectedStation;

        //const currentStation = selectedStation;
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
                //content_tosend.push(wanted_imgUrl)
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
      }
    );

    const data = await res.json();
    console.log(data)

    setResult(data);
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
              //submitHandler()
            }}
          />
          <button className=" pt-1 justify-center text-white text-sm font-bold bg-indigo-400 w-18 h-8 rounded-xl inset-shadow-sm inset-shadow-indigo-300 shadow-sm shadow-indigo-500" onClick={submitHandler}>
            Submit
          </button>
    </div>
  );
}
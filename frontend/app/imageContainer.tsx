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

  const [result, setResult] = useState<any>(null);
  const [prevCam, setprevCam] = useState("");
  let wanted_imgUrl = "";

  async function submitHandler(station, selectedFile) {
    const formData = new FormData();

    if (selectedFile) {
      formData.append("file", selectedFile);
      console.log("formdata, in file", formData)
    }

    if (station) {
        setprevCam(station)
        if(station.includes(prevCam) == true && prevCam.length > 0){
            const res = await fetch(`http://localhost:8000/camera/${prevCam}`);
            const camdata = await res.json();
            const camdata_arr =  Object.values(camdata.properties.presets);
            camdata_arr.forEach(function (x, i){
            if(x.id.includes(station)){
                wanted_imgUrl = x.imageUrl;
                console.log("clicked url, ", wanted_imgUrl)
             }
            }
          );
        }


      formData.append(
        "urlname",
        wanted_imgUrl
      );
    }

    const res = await fetch(
      "http://localhost:8000/predict",
      {
        method: "POST",
        body: formData,
      }
    );

    const data = await res.json();

    setResult(data);
  }

  return (
    <div className="grid md:grid-cols-3 pl-4 sm:w-10 md:w-full gap-2">
      <FormImage
        onFileSelect={(file) => {
          setSelectedFile(file);
          console.log(file)
        }}
      />
          <ImageSearch
            stations={stations}
            selectedStation={selectedStation}
            onStationSelect={(station) => {
              submitHandler(station)
            }}
          />
      <Link className="pr-2" href="/predict">
          <button className="pt-1 justify-center text-white text-sm font-bold bg-indigo-400 w-18 h-8 rounded-xl inset-shadow-sm inset-shadow-indigo-300 shadow-sm shadow-indigo-500" onClick={submitHandler}>
            Submit
          </button>
      </Link>
    </div>
  );
}
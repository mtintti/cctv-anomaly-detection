/*'use server'
import React from 'react';
//import { useState, useEffect } from 'react'
import FormImage from './form-component'
import ImageSearch from './cctvImageSearch'

interface StationsRes {
  features: Station[];
}
type Stations = {
    kind: "";
    features: Station[];
    };

type imgfile = {
    kind: "file";
    form_input
    };

type messagePostOptions = Stations | imgfile;
export default async function ImageContainer() {
  //const [postData, setPostData] = useState<any>(null);

    const stationsAll = await fetch("http://localhost:8000/stations", {cache: 'no-store'});
    const stationdata: StationsRes = await stationsAll.json();

   async function submit_handler(event: FormEvent<HTMLFormElement>) {
    console.log(event)
    event.preventDefault()

        const form_input = new FormData(event.currentTarget)
        const res = fetch('http://localhost:8000/predict', {
            method: 'POST',
            body: form_input})
        console.log("POST fetch request made")
        console.log(res)
        if(!res.ok){
            throw new Error('Failed to submit the data. Please try again.')}
        const res_data = res.json();
        data_gotFromPost(res_data)
        redirect("/predict")

        console.log("POST fetch request sent to data_gotFromPost")
        console.log(res_data)
        console.log("res data got ",res_data.filename, " ", res_data.filesize, " ", res_data.filetype);

}
//onSubmit={(submit_handler)}
  return (
    <div>
      <FormImage />
      <ImageSearch stations={stationdata.features}/>
      <button type='submit'>button</button>
      <div className="mt-4">
        {postData ? (
            <div>
              <h4>POST Response (Client tilassa):</h4>
              <p className="pt-3">{postData.filename}</p>
              <p className="pt-3">{postData.filecontent}</p>
              <p className="pt-3">{postData.filesize}</p>
              <img src="https://weathercam.digitraffic.fi/C0153502.jpg"/>
            </div>
        ) : (
          <p> </p>
        )}
      </div>

    </div>
  )
}*/

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

  async function submitHandler() {
    const formData = new FormData();

    if (selectedFile) {
      formData.append("file", selectedFile);
    }

    if (selectedStation) {
      formData.append(
        "stationId",
        selectedStation.id
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
    <div className="grid grid-flow-col grid-cols-3 gap-4">
      <FormImage
        onFileSelect={(file) => {
          setSelectedFile(file);
          console.log(file)
          //setSelectedStation(null);
        }}
      />
          <ImageSearch
            stations={stations}
            onStationSelect={(station) => {
              setSelectedStation(station);
              console.log(station)
              //setSelectedFile(null);
            }}
          />
      <Link href="/predict">
          <button onClick={submitHandler}>
            Submit
          </button>
      </Link>
    </div>
  );
}
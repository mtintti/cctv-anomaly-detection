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
    <div className="grid grid-flow-col grid-cols-3 pl-4 gap-2">
      <FormImage
        onFileSelect={(file) => {
          setSelectedFile(file);
          console.log(file)
          //setSelectedStation(null);
        }}
      />
          <ImageSearch
            stations={stations}
            selectedStation={selectedStation}
            onStationSelect={(station) => {
              setSelectedStation(station);
              console.log(station)
              //setSelectedFile(null);
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
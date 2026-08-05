"use client";

import { useState, useContext } from "react";
import {Context} from './providers/tanstack'
import Link from 'next/link'
import { redirect } from 'next/navigation'
import {setCookieServerAction} from './actions/cookies'
import FormImage from "./form-component";
import ImageSearch from "./cctvImageSearch";
import AvatarProfile from "./avatar"
import { ArrowUpDown, animateOnHover } from '../components/animate-ui/icons/arrow-up-down'

export default function ImageContainer({
  stations,
  result
}) {
  const [selectedFile, setSelectedFile] =
    useState<File | null>(null);

  const [selectedStation, setSelectedStation] =
    useState<Station | null>(null);

  const [selectedBaseId, setSelectedBaseId] = useState(null);
   const {errormodelSeeable,setErrormodelSeeable, pending, setPending} = useContext(Context);

  const content_tosend = [];
  let wanted_imgUrl = "";
  let generated_predictID = crypto.randomUUID();
    console.log("generated_predictID done?? ", generated_predictID)
    console.log("type of ", typeof(generated_predictID))

  async function submitHandler() {
    const formData = new FormData();

    formData.append("generated_predictID", generated_predictID);
    console.log("formdata contents, ", Object.entries(formData)[0]);

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
    console.log([formData.entries()])

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
    console.log("data gotten from /predict",data)
    console.log("task?? ", data['id of task'])
    setCookieServerAction("task_id",data['id of task'] )
    var predict_id = data.predict_id
    const byteSize = (str) => new Blob([str]).size;
    console.log(byteSize(data))



    if(predict_id){
        setErrormodelSeeable(false)
        setPending(true)
        redirect(`/predict/${predict_id}`)
    }

  }

  async function movinghome(){
    redirect('/')
  }

  return (
      <div className="flex items-baseline pl-4 min-w-[360px]">
        <button className="text-lg" onClick={movinghome}>home</button>

        <div className="grid grid-cols-3 justify-items-center gap-3 pb-2 w-full">
          <FormImage
            onFileSelect={(file) => {
              setSelectedFile(file);
              console.log("from formImage, ", file)
              console.log("in formImage's selectedFile", selectedFile)
            }}
          />
          <div className="ml-4 grid grid-cols-2 w-40 md:w-80">
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
              <button className="justify-self-end justify-center self-center rounded-full px-2 items-center z-40
               hover:scale-120 transition transform 0.3s ease-in-out"
              onClick={submitHandler}>
                <ArrowUpDown className="h-7 w-5 cursor-pointer"/>
              </button>
          </div>
          <AvatarProfile/>
              {/*<button className="pt-1 justify-center text-white text-sm text-shadow-md text-shadow-slate-400/60 font-bold bg-purple-100 w-10 h-8 rounded-xl inset-shadow-sm inset-shadow-indigo-100 shadow-sm shadow-purple-400" onClick={submitHandler}>
                Submit
              </button>*/}
        </div>
      </div>
  );
}
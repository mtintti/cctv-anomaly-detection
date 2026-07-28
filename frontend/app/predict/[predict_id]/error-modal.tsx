import Image from "next/image";
import predictedImage from "../../../public/prediction-v9.jpg"
import cameraIcon from "../../../public/3dicons-camera-dynamic-clay.png"
import React, { useState, useContext, useEffect } from "react";
import {Context} from '../../providers/tanstack'


export default function ErrorModal(errormodalMessage){


console.log("error message passed ErrorModal", errormodalMessage)
return(
    <div className="text-shadow-sm/20 tracking-wide text-pretty text-sm font-sm md:text-base md:font-base flex w-full h-[340px] md:h-[400px] overflow-hidden bg-red-50 justify-center inset-shadow-sm inset-shadow-red-400/50">
        {errormodalMessage.errormodalMessage == 404 ?
            <div className="gap-2 flex-col mt-40 z-3">
             <Image
                    src={cameraIcon}
                    alt="3D camera icon for dynamic visuality"
                    fill
                    className="object-cover blur-sm brightness-75 relative duration-500 hover:scale-103 hover:-translate-2" //overflow-hidden?
                  />
             <div className="absolute text-slate-800">
                <p>Choosen image was not completed fully,</p>
                <div className="gap-2 flex">
                    <p> image returned</p>
                    <p className="underline italic hover:decoration-sky-500">
                      {errormodalMessage.errormodalMessage}
                    </p>
                </div>
             </div>
            </div>
            :
            <>
            <div className="relative w-full h-[340px] md:h-[400px] overflow-hidden">
              <Image
                src={predictedImage}
                alt="Background prediction image"
                fill
                className="object-cover blur-sm brightness-100"
              />

                   <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-300">
                    <p>Chosen image was received earlier as its state is</p>
                    <p className="underline italic hover:decoration-sky-500">
                      {errormodalMessage.errormodalMessage}
                    </p>
                    <p className="pl-5 md:pl-0">but the images predictions have been deleted from Redis.</p>
                  </div>

            </div>
           </>
        }
    </div>
    )
}

/*
  <div className="flex gap-2">
                   <p>choosen images state of being processed is</p>
                   <p className="underline italic hover:decoration-sky-500">{errormodalMessage.errormodalMessage}</p>
                   <p> but images are deleted in Redis</p>
                </div>
 */
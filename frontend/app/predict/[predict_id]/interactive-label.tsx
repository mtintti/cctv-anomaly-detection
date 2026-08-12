import React, { useState, useContext, useEffect, useRef } from "react";
import sidebar from "../../../public/sidebar.png"
import { Init } from "./canvas";

export default function InteractiveLabeling({setopen_interactiveLabel, predictionCardData, clicked_index, setClicked_index}){
    const [openSidebar, setopenSidebar] = useState(false)
    const [hidbbox, sethidbbox] = useState(false)
    const [hidseg, sethidseg] = useState(false)
    const [dragging_bbox, setdragging_bbox] = useState(false)

    const imageRef = useRef(null);
    const canvasRef = useRef(null);
    const image = imageRef.current;
    const canvas = canvasRef.current;

   const visibility_dragging_bbox = () => {
        setdragging_bbox((prev) => !prev);
    };

    useEffect(() => {
        if (!dragging_bbox) return;

        const image = imageRef.current;
        const canvas = canvasRef.current;
        if (!image || !canvas) return;

        const initialize = () => Init(image, canvas);

        if (image.complete) {
            initialize();
        } else {
            image.addEventListener("load", initialize);
            return () => image.removeEventListener("load", initialize);
        }
    }, [dragging_bbox, clicked_index]);

    const visibility_bbox = () => {
        sethidbbox((prev) => !prev);
    };

    const visibility_seg = () => {
        sethidseg((prev) => !prev);
    };


    return(
        <>
        <div className="fixed inset-0 z-50 flex">
        <p className="absolute right-4 top-2 scale-110 cursor-pointer" onClick={() => setopen_interactiveLabel(false)}>x</p>

        <div className="max-lg:hidden flex-shrink-0 w-1/4 h-screen bg-gray-300"></div>

        <p className="lg:hidden absolute left-4 top-2 scale-110 cursor-pointer" onClick={() => setopenSidebar(true)}>x</p>
        {openSidebar && (
            <div className="lg:hidden fixed inset-0 z-20 w-1/2 h-screen bg-gray-300">
                <div className="flex justify-end bg-yellow-50 mr-4 mt-2 py-1 px-1" onClick={() => setopenSidebar(false)}>
                    <img src={sidebar} />
                </div>
            </div>
        )}

        <div className="flex-1 flex flex-col md:flex-row overflow-y-auto">
        <div className="flex flex-col w-full lg:w-4/5">
            <div className="relative mt-8 min-h-44 md:h-84 lg:h-3/5 bg-red-100">
                {predictionCardData[clicked_index].jsonresponse[0].prediction[0].imageBbox && (
                    <>
                        <img ref={imageRef} id="full-image" className="absolute w-full h-full" src={predictionCardData[clicked_index].jsonresponse[0].original_img} />
                        {hidbbox === false && (<img className="absolute w-full h-full" src={predictionCardData[clicked_index].jsonresponse[0].prediction[0].imageBbox} />)}
                        {hidseg === false && (<img className="absolute w-full h-full" src={predictionCardData[clicked_index].jsonresponse[0].prediction[0].imageSeg} />)}
                    </>
                )}
                {dragging_bbox === true && (<canvas ref={canvasRef} id="canvas" className="absolute h-auto w-full" />)}
                </div>
                <div className="flex relative mt-2 mb-2 left-8 flex min-w-28 max-w-68 py-1 px-1 rounded-full bg-slate-200 shadow-md shadow-slate-400 gap-2">
                <div className="justify-start w-full flex gap-2">
                    <div className="py-1 rounded-full bg-slate-100 ease-in-out hover:scale-95 text-sm hover:bg-slate-50" onClick={visibility_bbox}>
                        bbox
                    </div>
                    <div className="py-1 px-1 rounded-full bg-slate-100 ease-in-out hover:scale-95 text-sm hover:bg-slate-50" onClick={visibility_seg}>
                         seg
                    </div>
                </div>
                <div className="justify-end w-full flex gap-2">
                    <div className="py-2 px-2 md:py-4 md:px-4 rounded-full bg-slate-100 ease-in-out hover:scale-95 hover:bg-slate-50" onClick={visibility_dragging_bbox}></div>
                    <div className="py-2 px-2 md:py-4 md:px-4 rounded-full bg-slate-100 ease-in-out hover:scale-95 hover:bg-slate-50"></div>
                </div>
                </div>
            </div>

            <div className="flex flex-row md:flex-col gap-2 mx-2 py-4 md:mt-4 overflow-x-auto lg:overflow-y-auto">
                {predictionCardData.map((curr, i) => (
                    <div key={i}
                        onClick={() => setClicked_index(i)}
                        className="flex-shrink-0 cursor-pointer h-10 w-18 md:h-16 md:w-24 relative ease-in-out hover:opacity-80 hover:scale-105">
                        <img className="absolute w-full h-full object-cover" src={predictionCardData[i].jsonresponse[0].original_img} />
                        <img className="absolute w-full h-full object-cover" src={predictionCardData[i].jsonresponse[0].prediction[0].imageBbox} />
                        <img className="absolute w-full h-full object-cover" src={predictionCardData[i].jsonresponse[0].prediction[0].imageSeg} />
                    </div>
                ))}
            </div>
        </div>
    </div>

        </>
    );

}
import React, { useState, useContext, useEffect, useRef } from "react";
import sidebar from "../../../public/sidebar.png"
import { Init, setActiveColorClassname } from "./canvas";


export default function InteractiveLabeling({setopen_interactiveLabel, predictionCardData, clicked_index, setClicked_index}){

    const colors = {0: [121, 212, 119, 255], 1:[234, 184, 133, 255], 2:[96, 112, 160, 255], 3: [75, 40, 163, 255], 4:[81,28,63, 255] }

    const [openSidebar, setopenSidebar] = useState(false)
    const [hidbbox, sethidbbox] = useState(false)
    const [hidseg, sethidseg] = useState(false)
    const [dragging_bbox, setdragging_bbox] = useState(false)
    const [vis_color_classname, set_vis_color_classname] = useState(false);
    const [color_classname, set_color_classname] = useState<number[] | null>(null);
    const [color_of_picker_window, set_color_of_picker_window] = useState(null)
    const [amount_of_BoundingBoxes, set_amount_of_BoundingBoxes] = useState(0);
    const [max_reached, setMax_reached] = useState(false);

    console.log("color choosen ", color_classname)

    const imageRef = useRef(null);
    const canvasRef = useRef(null);
    const image = imageRef.current;
    const canvas = canvasRef.current;
    console.log("canvasRef ",canvasRef)

   const visibility_dragging_bbox = () => {
        setdragging_bbox((prev) => !prev);
   };

   useEffect(() => {
        if (!dragging_bbox) return;

        const image = imageRef.current;
        const canvas = canvasRef.current;
        if (!image || !canvas) return;

        const initialize = () => Init(image, canvas);
        if (!imageRef.current || !canvasRef.current) return;
          return Init(imageRef.current, canvasRef.current, (updatedRects) => {
              console.log("updatedRects was ", updatedRects)
              console.log("updatedRects type ", typeof(updatedRects))
              if(updatedRects.length <= 5){
                  set_amount_of_BoundingBoxes(updatedRects.length);
                  setMax_reached(false)
              } else {
                  console.log("max reached")
                  set_amount_of_BoundingBoxes(updatedRects.length);
                  setMax_reached(true)
              }
          });

        if (image.complete) {
            initialize();
        } else {
            image.addEventListener("load", initialize);
            return () => image.removeEventListener("load", initialize);
        }

   }, [dragging_bbox, clicked_index]);

console.log("color_classname is ", color_classname)
console.log("color_of_picker_window is ", color_of_picker_window)
    if(color_classname != null){
           if (!dragging_bbox) return;
           if (!canvasRef.current) return;
          setActiveColorClassname(color_classname);
          console.log("useEffect color change")
    set_color_of_picker_window(color_classname)
    set_color_classname(null)
   }

    const visibility_bbox = () => {
        sethidbbox((prev) => !prev);
    };

    const visibility_seg = () => {
        sethidseg((prev) => !prev);
    };
    const visibility_color_for_class_select = () => {
        set_vis_color_classname((prev) => !prev);
    };


    return(
        <>
        <div className="fixed inset-0 z-50 flex">
        <p className="absolute right-4 top-1 rounded-full px-2 hover:bg-white/40 scale-110 cursor-pointer" onClick={() => setopen_interactiveLabel(false)}>x</p>

        <div className="max-lg:hidden flex-shrink-0 w-1/4 h-screen bg-gray-300"></div>

        <p className="lg:hidden absolute left-4 top-3 scale-110 cursor-pointer" onClick={() => setopenSidebar(true)}><img width="10" src="/right-arrow.png"/></p>
        {openSidebar && (
            <div className="lg:hidden fixed inset-0 z-20 w-1/2 h-screen bg-gray-300">
                <div className="flex justify-end mr-4 mt-2">
                <div className="py-1 px-1 hover:bg-white/40" onClick={() => setopenSidebar(false)}>
                    <img width="15" src="/sidebar.png"/>
                </div>
                </div>
            </div>
        )}

        <div className="flex-1 flex flex-col md:flex-row md:pl-10 overflow-y-auto">
        <div className="flex flex-col lg:ml-8 lg:w-4/5">
            <div className="relative mt-8 min-h-44 md:h-84 lg:h-3/5">
                {predictionCardData[clicked_index].jsonresponse[0].prediction[0].imageBbox && (
                    <>
                        <img ref={imageRef} id="full-image" className="absolute w-full h-full" src={predictionCardData[clicked_index].jsonresponse[0].original_img} />
                        {hidbbox === false && (<img className="absolute w-full h-full" src={predictionCardData[clicked_index].jsonresponse[0].prediction[0].imageBbox} />)}
                        {hidseg === false && (<img className="absolute w-full h-full" src={predictionCardData[clicked_index].jsonresponse[0].prediction[0].imageSeg} />)}
                    </>
                )}
                {dragging_bbox === true && (<canvas ref={canvasRef} id="canvas" className="absolute h-auto w-full" />)}
                </div>
                <div className="items-center flex">
                    <div className="flex relative mt-2 mb-2 left-8 w-50 md:min-w-80 md:max-w-90 rounded-full bg-slate-200 shadow-md shadow-slate-400 gap-2">
                        <div className="justify-start w-full flex gap-2">
                            <div className="pt-1 ml-2 md:pt-2 px-1 rounded-md ease-in-out hover:bg-slate-300/30" onClick={visibility_bbox}>
                                <img width="40" src="/boundingbox.png"/>
                            </div>
                            <div className="pt-2 lg:pt-3 px-1 rounded-md ease-in-out hover:bg-slate-300/30" onClick={visibility_seg}>
                               <img width="40" src="/segmenticon2.png"/>
                            </div>
                        </div>
                        <div className="justify-end w-full flex gap-2">
                            <div className="py-2 px-2 md:py-3 md:px-3 rounded-md ease-in-out hover:bg-slate-300/30" onClick={visibility_dragging_bbox}><img width="25" src="/transform.png"/></div>
                            {color_of_picker_window != null ? <>
                                 <div
                                 style={{
                                    backgroundColor: `rgba(${color_of_picker_window[0]}, ${color_of_picker_window[1]}, ${color_of_picker_window[2]}, ${color_of_picker_window[3] / 255})`}}
                                  className="my-2 px-3 lg:px-4 lg:my-3 rounded-md inset-shadow-xs inset-shadow-slate-600 ease-in-out mr-4 bg-purple-400/80 hover:inset-shadow-slate-400" onClick={visibility_color_for_class_select}></div>
                                {vis_color_classname === true && (<div className="-top-10 absolute flex flex-wrap rounded-sm">
                                    {Object.values(colors).map((colors_available, i) => (<div key={i} style={{
                                    backgroundColor: `rgba(${colors_available[0]}, ${colors_available[1]}, ${colors_available[2]}, ${colors_available[3] / 255})`}}
                                    className="rounded-sm ease-in-out hover:shadow-md/30 hover:scale-90 w-6 h-6 ml-1 mr-1 my-1"
                                    onClick={() => set_color_classname(colors_available)}></div>) )}
                                 </div>
                                )}
                                </>
                                : <>
                                <div className="my-2 px-3 lg:px-4 lg:my-3 rounded-md inset-shadow-xs inset-shadow-slate-600 bg-purple-400/80 ease-in-out mr-4 hover:inset-shadow-slate-400" onClick={visibility_color_for_class_select}></div>
                                {vis_color_classname === true && (<div className="-top-10 absolute flex flex-wrap rounded-sm">
                                    {Object.values(colors).map((colors_available, i) => (<div key={i} style={{
                                    backgroundColor: `rgba(${colors_available[0]}, ${colors_available[1]}, ${colors_available[2]}, ${colors_available[3] / 255})`}}
                                    className="rounded-sm ease-in-out hover:shadow-md/30 hover:scale-90 w-6 h-6 ml-1 mr-1 my-1"
                                    onClick={() => set_color_classname(colors_available)}></div>) )}
                                 </div>
                                )}
                                </> }
                            </div>
                    </div>
                     <div className="ml-10 mt-2 text-gray-600 text-sm">
                         <p>bbox limit</p>
                         <div className="flex justify-center gap-1">
                           <div className={`${max_reached ? 'text-orange-900' :''}`}>{amount_of_BoundingBoxes}</div>
                           <p>/ 5</p>
                         </div>
                     </div>
                     <div className="ml-2 md:ml-40 text-sm text-gray-700 hover:bg-purple-300 bg-purple-200 inset-shadow-sm shadow-xs rounded-md px-3 py-1 justify-center">
                        <button className="cursor-pointer">send</button>
                     </div>
                </div>

            </div>

            <div className="flex flex-row md:flex-col gap-2 mx-2 py-4 md:mt-4 lg:ml-4 overflow-x-auto lg:overflow-y-auto">
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
import { Fallback_ui } from './lib/fallback_ui'


export default function Skeleton(skeletonMessage){

    console.log("Fallback_ui curr ", Fallback_ui[0])
    const clicked_index = 0

    return(
        <div className="bg-gray-100 md:py-3 md:px-3 inset-shadow-sm inset-shadow-gray-300 grid md:grid-cols-2">
                        <div className="">
                            <div className={`relative w-[360px] md:w-[700px] md:h-[400px] lg:w-[800px] h-[340px] shadow-xl shadow-gray-200 animate-pulse`}>
                            {skeletonMessage.skeletonMessage === 'running' &&

                  <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-400">
                    <p>Chosen image's processing state is {skeletonMessage.skeletonMessage}</p>
                    <p>working on image's number</p>
                    <p className="underline italic hover:decoration-sky-500">

                    </p>
                  </div>
                    }
                        </div>
                        </div>
                        <div className="col-span-2  md:col-span-2 bg-gray-300">
                            <div className="justify-center">
                                {Fallback_ui.map((curr, i) => (
                                    <div key={i}
                                     onClick={() => setClicked_index(i)}
                                     className={`relative pr-1 flex animate-pulse ${i==clicked_index ? 'bg-gray-200' :'bg-slate-400'} h-full inline-block font-extralight px-2 pt-1 mt-3`}>
                                        {Fallback_ui[i].jsonresponse[0].details[0].class_name}
                                    </div>
                                ))}
                                <div className="w-[360px] md:w-[700px] lg:w-[800px] font-normal bg-gray-200 animate-pulse pb-4">
                                    <div className="pl-10 pt-4 pr-10 grid grid-rows-1 tracking-tight font-bold">
                                    <p className="pb-2 text-xl font-medium animate-pulse">{Fallback_ui[clicked_index].jsonresponse[0].belongsto}</p>
                                    <div className="grid row-start-2 pt-2">
                                        <p className="font-light text-md pb-2 animate-pulse w-48 h-4 py-2 rounded-sm bg-slate-300 inset-shadow-sm inset-shadow-gray-400/30"> </p>
                                        <p className="font-light text-md mt-4 animate-pulse w-38 h-4 py-2 rounded-sm bg-slate-300 inset-shadow-sm inset-shadow-gray-400/30"> </p>
                                        </div>
                                         <div className="grid pr-10 row-start-2">
                                            <p className="pb-2 animate-pulse w-8 h-4 py-2 rounded-sm bg-slate-300 inset-shadow-sm inset-shadow-gray-400/30"> </p>
                                            <p className="pb-2 mb-2 animate-pulse w-8 h-4 py-2 mt-2 rounded-sm bg-slate-300 inset-shadow-sm inset-shadow-gray-400/30"> </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
    )
}
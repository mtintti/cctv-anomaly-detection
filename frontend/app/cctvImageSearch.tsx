"use client";

import { useState, ReactNode } from "react";

type Props = {
  stations: Station[];
  onStationSelect: (station: Station) => void;
};

 const Conditional = ({
      showWhen,
      children,
      } : {
          showWhen: boolean;
          children: ReactNode;
      }) => {
          if (showWhen) return <>{children}</>;
          return <></>;
      };


export default function ImageSearch({
  stations,
  onStationSelect,
  selectedStation,
}: Props) {


  const [search, setSearch] = useState("");
  const [smallerScroll, setsmallerScroll] = useState([]);
  const  [sidescrollOpen, setSidescrollOpen] = useState(false)
  const showSearchRes = search.length > 3;

  const filtered = stations.filter((station) =>
      station.properties.name
      .toLowerCase()
      .includes(search.toLowerCase())
  );

function parsingchoice(station){
    console.log("in parsingchoice")
  if(station){

      if(Object.hasOwn(station, "type") == true){
        setSidescrollOpen(true)
        onStationSelect(station.id)
        setsmallerScroll(station)
      } else {
        setSidescrollOpen(false)
        onStationSelect(station)
      }
    }
}

  return (
    <div className="z-10 relative">
     <input className="flex justify-start pt-1 pl-4 sm:20 md:w-full h-8 rounded-xl shadow-sm shadow-gray-300"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search station"
      />
     <Conditional showWhen={showSearchRes}>

      {/*first dropdown*/}
      <ul className="bg-gray-200 absolute -right-40 w-full mt-2 max-h-100 rounded-md scroll-smooth scrollbar-thumb-slate-900/60 scrollbar-track-slate-200/10 overflow-y-auto inset-shadow-sm inset-shadow-gray-300">
        {filtered.map((station) => (
          <li
            key={station.id}
            onClick={() => parsingchoice(station)}
            onDoubleClick={() => parsingchoice(station.properties.presets)}
          >
          <div className="pl-4 pt-3 pb-2 rounded-md hover:bg-indigo-50 hover:shadow-md hover:shadow-indigo-100 focus:bg-indigo-50 focus:shadow-md focus:shadow-indigo-100 ">
             <div className="relative flex inline-block text-sm font-extralight ">
                 <div className="">
                    {station.properties.name}
                 </div>
                <span className="absolute -top-2 -right-4 flex items-center justify-center w-5 h-5 rounded-full bg-indigo-400 shadow-sm shadow-indigo-500 text-indigo-200 font-extralight text-xs">
                    {station.properties.presets.length}
                </span>
             </div>
          </div>
          </li>
        ))}
      </ul>

      {/*second dropdown*/}
      {smallerScroll && sidescrollOpen == true ?
      <ul className="bg-gray-200 absolute m-8 w-30 mt-2 max-h-100 rounded-md scroll-smooth scrollbar-thumb-slate-900/60 scrollbar-track-slate-200/10 overflow-y-auto inset-shadow-sm inset-shadow-gray-300">
        {smallerScroll.properties.presets.map((invi) => (
          <li
            key={invi.id}
            onClick={() => parsingchoice(invi.id)}
          >
          <div className="pl-4 pt-3 pb-2 rounded-md hover:bg-indigo-50 hover:shadow-md hover:shadow-indigo-100 ">
             <div className="relative flex inline-block text-sm font-extralight ">
                 <div className="">
                    {invi.id}
                 </div>
             </div>
          </div>
          </li>
        ))}
      </ul> :
       <></>
      }
     </Conditional>
    </div>
  );
}
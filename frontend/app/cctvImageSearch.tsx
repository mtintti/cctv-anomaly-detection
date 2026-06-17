/*'use client'
import React from 'react';
import {FormEvent, onChange, useState} from 'react'
import { redirect } from 'next/navigation';

type FormImageProps = {
  data_gotFromPost: (data: any) => void;
};


export default function ImageSearch({stations}){

     const [searchfilter, setSearchfilter] = useState("");
    function searchres(event) {
        const searchstring = event.target.value.toLowerCase();
        console.log("written name", searchstring)
        const resultsearch = stations.filter((stat) => stat.properties.name.toLowerCase().includes(searchstring));
        //console.log("searched name", resultsearch.properties.name)
        //console.log("\n whole station", stat.properties.name)
        setSearchfilter(resultsearch);
        }


    return(
        <form>
      <input type='text' name='file' onChange={searchres} accept='text/plain'></input>
      </form>
      )
}*/

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
}: Props) {


  const [search, setSearch] = useState("");
  const showSearchRes = search.length > 3;

  const filtered = stations.filter((station) =>
      station.properties.name
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  const filteredId = filtered.filter((stationId) =>
    stationId.properties.presets[0].length
  );
  console.log("filtered ids, ", filteredId)


  function idForStation(itemNum: item.properties.presets.length, inx){
      console.log(inx, " and itemNum ", itemNum);
      /*while(itemNum){
          console.log("item in inx ", inx, " ", itemNum)
          inx--;
          }*/

      }
  if(filtered.length != 0 && showSearchRes){
    filteredId.forEach(idForStation);
  }

  console.log("filtered search, ",filtered.length)
  //console.log("filteredId search, ",filteredId)
  if(showSearchRes){
       console.log("filtered is more than 4 ",search.length);
  };
    //const filteredchilds = filtered.filter((invi) => invi.properties.presets);

//console.log("filtered child, " ,filteredchilds[0].properties.presets)
  return (
    <>
     <input className="w-96 h-8 bbg-gray-100 pl-4 rounded-xl shadow-sm"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search station"
      />
     <Conditional showWhen={showSearchRes}>

      <ul>
        {filtered.map((station) => (
          <li
            key={station.id}
            onClick={() => onStationSelect(station)}
          >
          <div className="pl-4 pt-1 rounded-md hover:bg-indigo-50 hover:shadow-md hover:shadow-indigo-100">
            {station.properties.name}
          </div>
          </li>
        ))}
        {/*{filteredchilds.map((invi) => (
            <li key={stations.id}>{invi.properties.presets[0].id}</li>
            ))}*/}
      </ul>
     </Conditional>
    </>
  );
}
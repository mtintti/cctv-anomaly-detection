'use client'
import React, { useState, useContext, useRef } from "react";
import { Toast } from '@base-ui/react/toast';

export default function AnnImg_detailed({setopen_clickedAnnImg_content,specified_AnnImg_content ,setSpecified_AnnImg_content}){
    const toastManager = Toast.useToastManager();

    return(
        <>
        <div className="fixed inset-0 z-50 flex mt-4">
        <p className="absolute right-4 top-1 rounded-full px-2 hover:bg-white/40 scale-110 cursor-pointer" onClick={() => setopen_clickedAnnImg_content(false)}>x</p>
        <div className="max-lg:hidden flex-shrink-0 w-full h-full place-items-center ">
            <div className="w-1/2 h-3/4 bg-slate-300 rounded-md py-2 px-2"><div className="h-full truncate bg-slate-200 shadow-md shadow-slate-600/30 rounded-md py-4 px-4 scrollbar-thin overflow-x-scroll ">{specified_AnnImg_content[0].annotations.map((ann, i) => (
                <div className="mb-2 text-left" key={i}>{ann}</div>
                ))}
            </div>
            </div>
        </div>
        </div>
        </>
    );

}
/*'use client'
import React, {FormEvent} from 'react'
import { redirect } from 'next/navigation';

type FormImageProps = {
  data_gotFromPost: (data: any) => void;
};


export default function FormImage(){

return(
    <form>
      <input type='file' name='file' accept='image/*'></input>
      </form>
    );

}*/

"use client";
import { useState,useRef, onClick } from "react";

type Props = {
  onFileSelect: (file: File) => void;
};

export default function FormImage({
  onFileSelect,
}: Props) {
    const fileInputLink = useRef("hey")
    //const fileInputLink = useRef<HTMLInputElement>(null);
    const [filename, setfilename] = useState("")

console.log("filestring , " , filename)
  return (
      <form className="flex justify-start pt-1 w-96 bbg-gray-100 h-8 pl-4 rounded-xl shadow-sm">
        <input
          type="file"
          hidden /*name="file" had this too, might still need it as fastapi endpoint predict expects a parameter of name as a file, will lead to unprocessed entity or bad request if no param*/
          onChange={(e) => {
            e.preventDefault();
            const file = e.target.files?.[0];
            //fileInputLink(file)
            setfilename(file.name)
            if (file) {
              onFileSelect(file);
            }
          }}
          ref={fileInputLink}
          accept="image/*"
        />
        <button className="text-gray-400"
    onClick={() => fileInputLink.current?.click()}>
    {filename || "Choose File, no File chosen" }
    </button>
    </form>

  );
}
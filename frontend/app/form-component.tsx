"use client";
import { useState,useRef, onClick } from "react";

type Props = {
  onFileSelect: (file: File) => void;
};

export default function FormImage({
  onFileSelect,
}: Props) {
    const fileInputLink = useRef("hey")
    const [filename, setfilename] = useState("")

console.log("filestring , " , filename)
  return (
      <div className="shadow-sm shadow-gray-300 pt-1 bbg-gray-100 pl-4 h-8 rounded-xl">
      <form >
        <input className="text-gray-400"
          type="file"
           name="file" /*had this too, might still need it as fastapi endpoint predict expects a parameter of name as a file, will lead to unprocessed entity or bad request if no param*/
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
    </form>
    </div>

  );
}
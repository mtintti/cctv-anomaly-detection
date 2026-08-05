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
// shadow-sm shadow-gray-300 pt-1 sm:max-w-48 bbg-gray-100 pl-4 h-8 rounded-xl
  return (
      <div>
      <form encType="multipart/form-data" className="pl-2">
        <input className="hidden"
          type="file"
           name="file" /*had this too, might still need it as fastapi endpoint predict expects a parameter of name as a file, will lead to unprocessed entity or bad request if no param*/
          onChange={(e) => {
            e.preventDefault();
            const file = e.target.files?.[0];
            console.log("file e.target.length, ", e.target.files?.length)
            //fileInputLink(file)
            setfilename(file.name)
            if (file) {
              onFileSelect(file);
            }
          }}
          ref={fileInputLink}
          accept="image/*"
        />
        <div onClick={() => fileInputLink.current?.click()}>
      {filename ? (
          <p className="mt-2 md:mr-40 text-sm text-gray-500 w-[50px] min-md:mr-10 min-md:min-w-[140px] lg:w-full bg-blue-100 max-sm:truncate min-sm:truncate">
            {filename}
          </p>
        )
        :
          <p className="text-gray-400 md:pl-3 px-2 shadow-sm shadow-gray-300 rounded-xl flex sm:inline-block justify-start pt-1 w-10 md:w-30 lr:w-80 h-8">file</p>
      }
        </div>
    </form>
    </div>

  );
}
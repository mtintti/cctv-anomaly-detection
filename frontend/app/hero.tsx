/*"use client";
import Image from 'next/image';
import baseImage from "../public/aerial-view-garden.jpg"
import segment_red from "../public/China_Drone_000823.png"
import segment_green from "../public/China_Drone_000823_2.png"
import segment_blue1 from "../public/China_Drone_000823_3.png"
import segment_blue2 from "../public/China_Drone_000823_4.png"
import {createContext, useContext} from "react";
import { useEffect, useState, useRef } from "react";

export default function ParallaxHero() {
const [ismouseEntered, setmouseEntered] = useState(false);
const MouseEnterContext = createContext<[boolean, React.Dispatch<React.SetStateAction<boolean>>] | undefined>(undefined);
const containerRef = useRef<HTMLDivElement>(null);
const ref = useRef<HTMLDivElement>(null);

const handleMouseEnter = () => {
    setmouseEntered(true);
    if(!containerRef.current) return
    };

 const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => { // [!code ++]
    if (!containerRef.current | ref.current) return;// [!code ++]
    const { left, top, width, height } =// [!code ++]
      containerRef.current.getBoundingClientRect();// [!code ++]
      ref.current.getBoundingClientRect();
    //const x = (e.clientX - left - width / 2) / 25;// [!code ++]
    //const y = (e.clientY - top - height / 2) / 25;// [!code ++]
    //console.log("x and y," , x ," ", y)
    console.log("translatez, ", translatez)
    containerRef.current.style.transform = `rotateY(${x}deg) rotateX(${y}deg) translateZ${translateZ}`;// [!code ++]
  };// [!code ++]

  const handleMouseLeave = () => {// [!code ++]
    if (!containerRef.current) return;// [!code ++]
    setmouseEntered(false);// [!code ++]
    containerRef.current.style.transform = `rotateY(0deg) rotateX(0deg)`;// [!code ++]
  };// [!code ++]

const useMouseContx = () => {
    const contx = useContext(useMouseContx);
    if(contx === undefined){
        throw new Error("useMouseContx needs to be within provider")
        }
    return contx;
    };

  return (
      <MouseEnterContext.Provider value={[ismouseEntered, setmouseEntered]}>
    <div className="relative w-full mt-5 transition-all duration-200 ease-linear" ref={containerRef} onMouseEnter={handleMouseEnter} onMouseMove={handleMouseMove} onMouseLeave={handleMouseLeave}  style={{perspective: "1000px", transformStyle: "preserve-3d",}} >
      <div className="absolute inset-x-0 top-10 z-20 text-shadow-sm text-shadow-indigo-400 text-slate-300 tracking-wider grid sm:grid-cols-3 justify-items-center">
        <p className="sm:text-2xl md:text-3xl lr:md:text-4xl font-bold">have you ever felt</p>
        <p className="sm:text-2xl md:text-3xl lr:md:text-4xl font-bold text-blue-900 bg-blue-100 px-1">roadbumps</p>
        <p className="sm:text-2xl md:text-3xl lr:md:text-4xl font-bold">along the way</p>
      </div>

      <div className="relative w-full aspect-[1500/800] overflow-hidden">
        <Image
          className="object-cover transition duration-200 ease-linear"
          ref={ref}
          translatez="200"
          alt="predicted, segmented mask image showing found anomalities"
          priority
          fill
          sizes="100vw"
          src={baseImage}
        />

        <div className="absolute z-10 top-[34%] -rotate-[20deg] left-[8%] w-[33%] h-[33%]">
          <Image className="object-contain" alt="red segmented anomaly mask" fill priority sizes="33vw" src={segment_red} />
        </div>

        <div className="absolute z-10 top-[20%] -rotate-[20deg] left-[39%] w-[60%] h-[60%]">
          <Image className="object-contain" alt="green segmented anomaly mask" fill priority sizes="60vw" src={segment_blue1} />
        </div>

        <div className="absolute z-10 top-[15%] rotate-[95deg] left-[30%] w-[40%] h-[40%]">
          <Image className="object-contain" alt="blue segmented anomaly mask" fill priority sizes="40vw" src={segment_blue2} />
        </div>

        <div className="absolute z-10 top-[32%] -rotate-[90deg] left-[30%] w-[40%] h-[40%]">
          <Image className="object-contain" alt="green segmented anomaly mask" fill priority sizes="40vw" src={segment_green} />
        </div>
      </div>
    </div>
    </MouseEnterContext.Provider>
  );
}

*/

"use client";
import Image from 'next/image';
import baseImage from "../public/aerial-view-garden.jpg";
import segment_red from "../public/China_Drone_000823.png";
import segment_green from "../public/China_Drone_000823_2.png";
import segment_blue1 from "../public/China_Drone_000823_3.png";
import segment_blue2 from "../public/China_Drone_000823_4.png";
import { useRef } from "react";

const tilt = 7;   // small, capped rotation
const onHoverScale = 1.10; // subtle zoom, not a real "pop"

export default function ParallaxHero() {
  const cardRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const card = cardRef.current;
    if (!card) return;

    const { left, top, width, height } = card.getBoundingClientRect();
    const px = (e.clientX - left) / width;  // 0..1 across the box
    const py = (e.clientY - top) / height;  // 0..1 down the box

    const rotateY = (px - 0.5) * 2 * tilt;
    const rotateX = -(py - 0.5) * 2 * tilt;

    card.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(${onHoverScale})`;
  };

  const handleMouseLeave = () => {
    const card = cardRef.current;
    if (!card) return;
    card.style.transform = `rotateX(0deg) rotateY(0deg) scale(1)`;
  };

  return (
    <div className="relative w-full mt-5 transition-transform duration-700 ease-in ease-out">
      <div className="absolute inset-x-0 top-10 z-20 text-shadow-sm text-shadow-indigo-400 text-slate-300 tracking-wider grid sm:grid-cols-3 justify-items-center">
        <p className="sm:text-2xl md:text-3xl lr:md:text-4xl font-bold">have you ever felt</p>
        <div className="sm:text-2xl md:text-3xl lr:md:text-4xl font-bold text-blue-900 bg-blue-100 px-1 hover:scale-110 hover:rotate-1 hover:motion-reduce">
        <p className="hover:scale-115">roadbumps</p>
        </div>
        <p className="sm:text-2xl md:text-3xl lr:md:text-4xl font-bold">along the way</p>
      </div>

      {/* outer box: crops to aspect ratio, hosts the perspective context */}
      <div
        className="relative w-full h-[65vh] md:h-auto md:aspect-[1500/800] overflow-hidden"
        style={{ perspective: "1200px" }}
      >
        {/* inner "3D stage": this is what actually rotates, no overflow-hidden here */}
        <div
          ref={cardRef}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          className="absolute inset-0  w-full h-[65vh] md:h-auto md:aspect-[1500/800] transition-transform duration-200 ease-out"
          style={{ transformStyle: "preserve-3d" }}
        >
          <Image
            className="object-cover"
            style={{ transform: "translateZ(0px)" }}
            alt="predicted, segmented mask image showing found anomalities"
            priority fill sizes="100vw" src={baseImage}
          />

          <div
            className="absolute top-[37%] -rotate-[20deg] left-[-4%] md:top-[34%] md:-rotate-[20deg] md:left-[8%] w-[33%] h-[33%] duration-500 hover:zoom-200"
            style={{ transform: "translateZ(25px)" }}
          >
            <Image className="object-contain" alt="red segmented anomaly mask" fill priority sizes="33vw" src={segment_red} />
          </div>

          <div
            className="absolute top-[13%] -rotate-[3deg] left-[46%] md:top-[20%] md:-rotate-[18deg] md:left-[39%] w-[60%] h-[60%] duration-500 hover:zoom-200"
            style={{ transform: "translateZ(15px)" }}
          >
            <Image className="object-contain" alt="green segmented anomaly mask" fill priority sizes="60vw" src={segment_blue1} />
          </div>

          <div
            className="absolute top-[15%] rotate-[95deg] left-[30%] w-[40%] h-[40%] duration-500 hover:zoom-200"
            style={{ transform: "translateZ(30px)" }}
          >
            <Image className="object-contain" alt="blue segmented anomaly mask" fill priority sizes="40vw" src={segment_blue2} />
          </div>

          <div
            className="absolute top-[32%] -rotate-[90deg] left-[30%] w-[40%] h-[40%] duration-500 hover:zoom-200"
            style={{ transform: "translateZ(30px)" }}
          >
            <Image className="object-contain" alt="green segmented anomaly mask" fill priority sizes="40vw" src={segment_green} />
          </div>
        </div>
      </div>
    </div>
  );
}
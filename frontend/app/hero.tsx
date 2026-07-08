
"use client";
import Image from 'next/image';
import baseImage from "../public/aerial-view-garden.jpg";
import segment_red from "../public/China_Drone_000823.png";
import segment_green from "../public/China_Drone_000823_2.png";
import segment_blue1 from "../public/China_Drone_000823_3.png";
import segment_blue2 from "../public/China_Drone_000823_4.png";
import { useRef } from "react";

const tilt = 7;
const onHoverScale = 1.10;

export default function ParallaxHero() {
  const cardRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const card = cardRef.current;
    if (!card) return;

    const { left, top, width, height } = card.getBoundingClientRect();
    const px = (e.clientX - left) / width;
    const py = (e.clientY - top) / height;

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

      <div
        className="relative w-full h-[65vh] md:h-auto md:aspect-[1500/800] overflow-hidden"
        style={{ perspective: "1200px" }}
      >
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
'use client'
import { useRouter } from 'next/navigation';
import { House } from "lucide-react";

export default function Homebutton(){
     const router = useRouter();

    async function movinghome(){
        router.push('/')
    }

    return(
        <>
            <div className="text-lg my-6 cursor-pointer pl-4" onClick={movinghome}><House/></div>
        </>
    )
}
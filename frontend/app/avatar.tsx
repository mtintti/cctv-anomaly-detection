'use client'
import { Avatar } from '@base-ui/react/avatar';
import { useRouter } from "next/navigation";
import { logout } from "@/app/actions/signout";


export default function AvatarProfile({session}){
    const router = useRouter();
    //const session = await auth();
    console.log("PROFILE SESSION ", session)
    function handle_clickAction(){
        if(!session){
            router.push("/auth/signin");
        } else if (session.user != undefined){
            console.log("LOGGING OUT")
            logout()
        }
    }

    return(
        <>
        <div className="relative group" onClick={() => handle_clickAction()}>
            <Avatar.Root className="absolute w-10 z-1 h-10 items-center justify-center cursor-pointer flex overflow-hidden rounded-full ease-out hover:scale-110 transition transform 0.3s ease-in-out">
                {session?.user && (<Avatar.Image src="https://images.unsplash.com/photo-1785821456526-5e9c4e5f1dd6?q=80&w=435&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" className="object-cover w-full scale-120 h-full" />)}
                {!session && (<Avatar.Image className="object-cover w-full h-full scale-80 opacity-60" src="https://images.unsplash.com/vector-1776244476031-db2aa624a2a0?q=80&w=580&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"></Avatar.Image>)}
            </Avatar.Root>
             {session?.user && (<div className="absolute z-0 inset-0 w-11 h-11 items-center justify-center flex overflow-hidden rounded-full bg-gradient-to-r from-zinc-300 to-mist-500 opacity-50 group-hover:duration-200 group-hover:opacity-100 blur"> </div>) }
        </div>
    </>

    )
}
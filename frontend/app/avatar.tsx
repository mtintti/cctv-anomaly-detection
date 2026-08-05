import { Avatar } from '@base-ui/react/avatar';
import { redirect } from 'next/navigation'

export default function AvatarProfile(){


    async function opening_modal(){
     redirect('/auth/signin')
    }
    console.log("setOpen in avatar ", open)
    return(
        <>
        <div className="relative group" onClick={opening_modal}>
         <Avatar.Root className="absolute w-10 z-1 h-10 items-center justify-center cursor-pointer flex overflow-hidden rounded-full ease-out hover:scale-110 transition transform 0.3s ease-in-out">
            <Avatar.Image
              src="https://images.unsplash.com/photo-1785821456526-5e9c4e5f1dd6?q=80&w=435&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
              className="object-cover w-full scale-120 h-full"
            />
            <Avatar.Fallback delay={600} className="flex justify-content h-full w-full align-center">
              LT
            </Avatar.Fallback>
          </Avatar.Root>
         <div className="absolute z-0 inset-0 w-11 h-11 items-center justify-center flex overflow-hidden rounded-full
          bg-gradient-to-r from-zinc-300 to-mist-500 opacity-50 group-hover:duration-200 group-hover:opacity-100 blur">
         </div>
    </div>
    </>

    )
}
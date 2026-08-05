'use client'
//import { authenticate } from '../../actions/authenticate';
//import { useActionState } from 'react';
import Homebutton from '@/components/homeButton'


export default function Signup(){
    //const [formAction] = useActionState(authenticate, undefined)


    return(
        <form className="z-4"> {/*action={formAction} */}
        <Homebutton/>
            <div className="absolute justify-center items-center w-full h-full py-4 bg-blue-200 inset-shadow-cyan-800/50 inset-shadow-lg rounded-sm">
                <div className="md-4 my-1 mr-4 place-self-end">
                    <p className="py-1 px-1 text-xl font-light text-slate-400 cursor-pointer"></p>
                </div>
                <div className="absolute bg-blue-50 inset-x-0 bottom-0 w-full h-1/5 rounded-t-lg">
                    <p className="text-center mt-8 py-4 px-4 rounded-full font-bold text-xl text-slate-500">signin</p>
                </div>
            </div>
        </form>
    );

}
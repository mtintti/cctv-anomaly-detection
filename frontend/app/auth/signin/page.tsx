
//import { authenticate } from '../../actions/authenticate';
//import { useActionState } from 'react';
import Homebutton from '@/components/homeButton'


export default function Signin(){
    //const [formAction] = useActionState(authenticate, undefined)



    return(
        <form className="z-4"> {/*action={formAction} */}
            <div className="absolute justify-center items-center w-screen h-full bg-blue-200 inset-shadow-cyan-800/50 inset-shadow-lg rounded-sm">
                <Homebutton/>

            </div>
        </form>
    );

}
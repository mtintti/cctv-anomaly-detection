'use client'
import { authenticate } from '../../actions/authenticate';
import { useActionState, useEffect } from 'react';
import Homebutton from '@/components/homeButton'
import Link from 'next/link'
import { useRouter } from 'next/navigation'


export default function Signin(){
    const [state, formAction, pending] = useActionState(authenticate, undefined)
    const router = useRouter()


    console.log("formAction login ", formAction)
    console.log("pending?? ", pending)
    console.log("state?? ", state)

    useEffect(() => {
        if(pending === false && state != undefined && state['success'] === true){
            router.push('/dashboard')
        }
    }, [pending, router])



    return(
        <div className="flex min-w-[360px] lg:w-screen lg:h-screen min-h-[530px] bg-zinc-100/30 p-1">
            <Homebutton />
                {/* Left side */}
                <div className="flex w-full flex-col justify-center md:px-12 md:w-1/2">

                  <form className="mt-8 flex flex-col" action={formAction}>
                    <input
                      type="text"
                      name="username"
                      placeholder="Username"
                      className="h-10 w-64 rounded-full hover:border bg-white px-4 shadow-lg/10 mb-2"
                    />
                    <p className="ml-8 text-slate-400">or</p>

                    <input
                      type="text"
                      name="email"
                      placeholder="Email"
                      className="h-10 w-64 rounded-full hover:border bg-white px-4 shadow-lg/10 mt-2"
                    />

                    <input
                      type="password"
                      name="password"
                      placeholder="Password"
                      className="h-10 w-64 rounded-full hover:border bg-white px-4 shadow-lg/10 mt-6"
                    />
                    {pending === false ?
                        <button className="py-2 py-2 w-64 rounded-md hover:bg-blue-200 mt-8 text-slate-200 hover:text-white font-lg bg-slate-400/60 shadow-md/10 hover:shadow-md/20">login</button>
                        : <button className="py-2 py-2 w-64 h-4 rounded-md hover:bg-blue-200 mt-12 text-slate-400 hover:text-white font-lg bg-slate-300/60 shadow-md/10 hover:shadow-md/20"></button>}
                    {state != undefined && state === 'Invalid credentials.' && (<p className="text-sm text-red-400 ml-8 mt-1">Invalid credentials, try again</p>)}
                  </form>
                  <div className="grid grid-cols-2 gap-2 sm:w-50">
                      <div className="w-full h-4 py-1 px-1 hover:bg-gray-200 rounded-full bg-gray-300 mt-8 shadow-lg/10"></div>
                      <Link className="w-4 h-4 py-1 px-1 hover:bg-gray-100 rounded-full bg-gray-200 mt-8" href={{pathname: '/auth/signup'}}></Link>
                  </div>
                </div>

            {/* Right side */}
            <div className="hidden md:block md:w-1/2 transition z-0 hover:z-1 origin-bottom ease-in-out translate-x-70 duration-400 hover:translate-x-44">
              <div className="h-full w-full rounded-md bg-blue-200 shadow-md shadow-blue-200/50" />
            </div>
            <div className="hidden md:block md:w-1/2 transition z-2 hover:z-1 origin-bottom ease-in-out duration-400 translate-x-37 hover:translate-x-8">
              <div className="h-full w-full rounded-md bg-blue-300 shadow-md shadow-blue-200/50" />
            </div>
            <div className="hidden md:block md:w-1/2 transition z-3 origin-bottom ease-in-out duration-400 hover:-translate-x-4">
              <div className="h-full w-full rounded-md bg-blue-400 shadow-md shadow-blue-200/50"/>
            </div>
        </div>
    );

}
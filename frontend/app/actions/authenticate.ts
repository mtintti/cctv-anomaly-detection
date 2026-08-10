'use server';

import { signIn } from '../lib/auth';
import { AuthError } from 'next-auth';


export async function authenticate(
  prevState: string | undefined,
  formData: FormData,
) {
  try {
   await signIn('credentials',  {
      ...Object.fromEntries(formData),
      redirect: false,
    });
   return { 'success': true};
  } catch (error) {
      console.log("error.type ", error)
    if (error instanceof AuthError) {
      switch (error.type) {
        case 'CredentialsSignin':
          return 'Invalid credentials.';
        case 'CallbackRouteError':
            console.log("error cause", error.cause['err'])
            console.log("error cause type", typeof(error.cause['err']))
            return error.cause['err']
        default:
          return 'Something went wrong.';
      }
    console.log("AuthError ",AuthError);
    }
    throw error;
  }
}
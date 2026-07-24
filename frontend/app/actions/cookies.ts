'use server'
import { cookies } from "next/headers";

export async function setCookieServerAction(key: string,value) {
    const cookieStore = await cookies();

    cookieStore.set(key, value);
    console.log("cookies set", key, " ",value)
}

import NextAuth from 'next-auth';
import { authConfig } from './auth.config';

export default NextAuth(authConfig).auth;

export const config = {
     matcher: ["/dashboard/:path*"],
  // https://nextjs.org/docs/app/api-reference/file-conventions/proxy#matcher
  //matcher: ['/((?!api|_next/static|_next/image|.*\\.png$).*)'],
};

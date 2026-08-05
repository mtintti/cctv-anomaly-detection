import NextAuth from 'next-auth';
import { authConfig } from './auth.config';
import Credentials from 'next-auth/providers/credentials';
import { z } from 'zod';
import bcrypt from 'bcrypt'


export const { auth, signIn, signOut } = NextAuth({
  ...authConfig,
  providers: [Credentials({
      async authorize(credentials){
          const credentials_after_parse = z.object({email: z.string().email(), password: z.string().min(5) })
          .safeParse(credentials);

          if(credentials_after_parse.success){
              const {email, password} = credentials_after_parse.data;
              const response = await fetch("http://localhost:8000/login", {
                  method: "POST",
                  headers: {
                    "Content-Type": "application/json",
                  },
                  body: JSON.stringify({
                    email,
                    password,
                  }),
                });

                const user = await response.json();

              if(!user) return null;
              const passwords_check = await bcrypt.compare(password, user_in_db.password);
              if(passwords_check == true) return user_in_db;
          }
      console.log("invalid credentials, not found or password was wrong")
      return null;
      },
    }),
  ],
});
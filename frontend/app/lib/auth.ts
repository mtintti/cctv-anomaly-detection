import NextAuth from 'next-auth';
import { authConfig } from './auth.config';
import Credentials from 'next-auth/providers/credentials';
import { z } from 'zod';
import bcrypt from 'bcrypt'


export const { auth, signIn, signOut } = NextAuth({
  ...authConfig,
  providers: [Credentials({
      async authorize(credentials){
          console.log("credentials in auth.ts ", credentials)
          if(credentials['callbackUrl'].includes('auth/signup')){

              const credentials_after_parse = z.object({username: z.string().min(2), email: z.string().email(), password: z.string().min(5) })
              .safeParse(credentials);

              if(credentials_after_parse.success){
                  var {username, email, password} = credentials_after_parse.data;
                  const salt_rounds = 10;
                  password = await bcrypt.hash(password, salt_rounds);
                  console.log("TO SEND POST", username, email, password)
                  const response = await fetch("http://localhost:8000/auth/signup", {
                      method: "POST",
                      headers: {
                        "Content-Type": "application/json",
                      },
                      body: JSON.stringify({
                        username,
                        email,
                        password,
                      }),
                  });

                    const user = await response.json();
                    console.log("user in auth.ts ", user)


                  if(!response.ok){
                      return null;
                  } else if (response.ok) {
                      return 'user created';
                  }
              } else if(!credentials_after_parse.success){
          console.log("invalid credentials, parsing was wrong in creating user")
          //var message = credentials_after_parse.error.issues[0]['message'] + credentials_after_parse.error.issues[1]['message'] + credentials_after_parse.error.issues[2]['message']; //JSON.stringify(credentials_after_parse.error.issues);
          console.log("username issue??")
          const errors = {
              username: "",
              email: "",
              password: "",
            };

            for (const issue of credentials_after_parse.error.issues) {
              console.log("issue ",issue)
              const name = issue.path[0]
              console.log("path ",name)

              if (name === "username" ||
                  name === "email" ||
                  name === "password") {
                errors[name] = issue.message;
              }
            }
          console.log(errors)
          var message = JSON.stringify(errors)
          throw new Error(message);
          }

          } else if (credentials['callbackUrl'].includes('auth/signin')){
              const credentials_after_parse = z.object({email: z.string().email(), password: z.string().min(5) })
              .safeParse(credentials);

              if(credentials_after_parse.success){
                  const {email, password} = credentials_after_parse.data;
                  console.log("TO SEND POST", email, password)
                  const response = await fetch("http://localhost:8000/auth/signin", {
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
                    console.log("user in auth.ts ", user)
                    var found_user_password = user[3]

                  if(user === null) return null;
                  console.log("passwords_check ", password, found_user_password)
                  console.log("passwords_check type ", typeof(password), typeof(found_user_password))
                  const passwords_check = await bcrypt.compare(password, found_user_password);
                  if(passwords_check == true) return 'login success';
              }

            console.log("invalid credentials, parsing was wrong in signin")
            console.log("invalid credentials, parsing was wrong in creating user")
            return credentials_after_parse.error.issues;
          }
      console.log("pathurl was not found, or other error")
      return null;
      },
    }),
  ],
});
import * as AWS from "aws-sdk";
import * as awsConfig from "../awsconfig";

import {
  getIdentityId,
  setAWSCreds,
  signIn,
} from "../hooks/useCognitoAuthv3";

import { useState } from "react";

const LoginPage = () => {
  const [username, setUserName] = useState("");
  const [password, setPassword] = useState("");
  const [loginFailed, setLoginFailed] = useState(false);

  const loginStatus = "Login Failed. Incorrect username or password.";
  AWS.config.region = awsConfig.REGION;

  const handleSignIn = async (e) => {
    e.preventDefault();
    try {
      const session = await signIn(username, password);
      if (session && typeof session.AccessToken !== "undefined") {
        sessionStorage.setItem("accessToken", session.AccessToken);
        await getIdentityId();
        const awsCreds = await setAWSCreds(); // get STS creds
        if (awsCreds) {
          window.location.href = "/Dashboard";
        }
      } else {
        console.error("SignIn session or AccessToken is undefined.");
      }
    } catch (error) {
      setLoginFailed(true)
    }
  };

  return (
    <div className="container text-center h-100" data-bs-theme="dark">
      <div className="row m-5 justify-content-center h-100">
        <div className="col-lg-4 col-sm-12">
          <div className="card shadow">
            <div className="card-header">
              <h1 className="h3 m-3 font-weight-normal">Cross-dock Demo Login</h1>
            </div>
            <div className="card-body">
              <label className="sr-only mt-2">Username</label>
              <input
                type="text"
                id="inputUser"
                className="form-control"
                placeholder="Username"
                value={username}
                onChange={(e) => setUserName(e.target.value)}
                required
                autoFocus
              />
              <label htmlFor="inputPassword" className="sr-only mt-2">
                Password
              </label>
              <input
                type="password"
                id="inputPassword"
                className="form-control"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              {loginFailed && (
                <div className="mt-2 alert alert-danger">{loginStatus}</div>
              )}
              <button
                className="mt-2 btn btn-lg btn-primary btn-block"
                onClick={handleSignIn}
                type="submit"
              >
                Sign in
              </button>
            </div>
          </div>
        </div>
      </div>
      <a href="https://aws.amazon.com/what-is-cloud-computing">
        <img
          src="https://d0.awsstatic.com/logos/powered-by-aws-white.png"
          alt="Powered by AWS Cloud Computing"
        />
      </a>
    </div>
  );
}

export default LoginPage;

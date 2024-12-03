import * as awsConfig from "../awsconfig";

import {
  CognitoIdentityClient,
  GetCredentialsForIdentityCommand,
  GetIdCommand,
} from "@aws-sdk/client-cognito-identity";
import {
  CognitoIdentityProviderClient,
  InitiateAuthCommand,
} from "@aws-sdk/client-cognito-identity-provider";

export const cognitoClient = new CognitoIdentityProviderClient({
  region: awsConfig.REGION,
});
export const cognitoIdClient = new CognitoIdentityClient({
  region: awsConfig.REGION,
});

// Define cogUri
export const cogUri = (() => {
  const uri = `cognito-idp.${awsConfig.REGION}.amazonaws.com/${awsConfig.COGNITO_USERPOOL}`;
  return () => uri;
})();


export const signIn = async (username, password) => {
  const params = {
    AuthFlow: "USER_PASSWORD_AUTH",
    ClientId: awsConfig.COGNITO_CLIENT_ID,
    AuthParameters: { USERNAME: username, PASSWORD: password },
  };

  const { AuthenticationResult } = await cognitoClient.send(new InitiateAuthCommand(params));
  if (AuthenticationResult) {
    const { IdToken, AccessToken, RefreshToken } = AuthenticationResult;
    sessionStorage.setItem("authTokens", JSON.stringify({ IdToken, AccessToken, RefreshToken }));
    return AuthenticationResult;
  }
};

let cachedIdentityId = null;
export const getIdentityId = async () => {
  if (cachedIdentityId) return cachedIdentityId;

  const { IdToken } = JSON.parse(sessionStorage.getItem("authTokens") || "{}");
  if (!IdToken) throw new Error("No ID token found");

  const params = {
    IdentityPoolId: awsConfig.COGNITO_ID_POOL_ID,
    Logins: { [cogUri()]: IdToken },
  };

  const { IdentityId } = await cognitoIdClient.send(new GetIdCommand(params));
  console.log("Identity ID:", IdentityId);
  sessionStorage.setItem("cognitoIdentityId", IdentityId);
  cachedIdentityId = IdentityId;
  return IdentityId;
};

let cachedCredentials = null;
export const setAWSCreds = async () => {
  if (cachedCredentials && new Date(cachedCredentials.expiration) > new Date()) {
    return cachedCredentials;
  }

  const { IdToken } = JSON.parse(sessionStorage.getItem("authTokens") || "{}");
  if (!IdToken) throw new Error("No ID token found");

  const IdentityId = await getIdentityId();
  const params = {
    IdentityId,
    Logins: { [cogUri()]: IdToken },
  };

  const { Credentials } = await cognitoIdClient.send(new GetCredentialsForIdentityCommand(params));
  const { AccessKeyId, SecretKey, SessionToken, Expiration } = Credentials;
  cachedCredentials = {
    accessKeyId: AccessKeyId,
    secretAccessKey: SecretKey,
    sessionToken: SessionToken,
    expiration: Expiration,
  };
  sessionStorage.setItem("AWSCredentials", JSON.stringify(cachedCredentials));
  return cachedCredentials;
};

export const getAWSCreds = () => {
  const creds = JSON.parse(sessionStorage.getItem("AWSCredentials") || "{}");
  if (creds.expiration) creds.expiration = new Date(creds.expiration);
  return creds;
};

export const refreshToken = async () => {
  const { RefreshToken } = JSON.parse(sessionStorage.getItem("authTokens") || "{}");
  if (!RefreshToken) throw new Error("No refresh token found");

  const params = {
    AuthFlow: "REFRESH_TOKEN_AUTH",
    ClientId: awsConfig.COGNITO_CLIENT_ID,
    AuthParameters: { REFRESH_TOKEN: RefreshToken },
  };

  const { AuthenticationResult } = await cognitoClient.send(new InitiateAuthCommand(params));
  if (AuthenticationResult) {
    const { IdToken, AccessToken } = AuthenticationResult;
    sessionStorage.setItem("authTokens", JSON.stringify({ IdToken, AccessToken, RefreshToken }));
    await getIdentityId();
    await setAWSCreds();
    return true;
  }
  return false;
};

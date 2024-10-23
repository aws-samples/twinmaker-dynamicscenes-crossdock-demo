import * as awsConfig from "../awsconfig";

import {
  CognitoIdentityClient,
  GetCredentialsForIdentityCommand,
  GetIdCommand,
} from "@aws-sdk/client-cognito-identity";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import {
  CognitoIdentityProviderClient,
  InitiateAuthCommand,
} from "@aws-sdk/client-cognito-identity-provider";

// ES Modules import

export const cognitoClient = new CognitoIdentityProviderClient({
  region: awsConfig.REGION,
});
export const cognitoIdClient = new CognitoIdentityClient({
  region: awsConfig.REGION,
});

export const cogUri =
  "cognito-idp." +
  awsConfig.REGION +
  ".amazonaws.com/" +
  awsConfig.COGNITO_USERPOOL;

export const signIn = async (username, password) => {
  const params = {
    AuthFlow: "USER_PASSWORD_AUTH",
    ClientId: awsConfig.COGNITO_CLIENT_ID,
    AuthParameters: {
      USERNAME: username,
      PASSWORD: password,
    },
  };
  try {
    const command = new InitiateAuthCommand(params);
    const { AuthenticationResult } = await cognitoClient.send(command);
    if (AuthenticationResult) {
      sessionStorage.setItem("idToken", AuthenticationResult.IdToken || "");
      sessionStorage.setItem(
        "accessToken",
        AuthenticationResult.AccessToken || ""
      );
      sessionStorage.setItem(
        "refreshToken",
        AuthenticationResult.RefreshToken || ""
      );
      return AuthenticationResult;
    }
  } catch (error) {
    throw error;
  }
};

export const getIdentityId = async () => {
  try {
    const params = {
      IdentityPoolId: awsConfig.COGNITO_ID_POOL_ID,
      Logins: {
        [cogUri]: sessionStorage.getItem("idToken"),
      },
    };
    const command = new GetIdCommand(params);
    const response = await cognitoIdClient.send(command);
    console.log("Identity ID:", response.IdentityId);
    sessionStorage.setItem("cognitoIdentityId", response.IdentityId);
    return response.IdentityId;
  } catch (error) {
    console.error("Error getting identity id: ", error);
    throw error;
  }
};

export const setAWSCreds = async () => {
  const params = {
    IdentityId: sessionStorage.getItem("cognitoIdentityId"),
    Logins: {
      [cogUri]: sessionStorage.getItem("idToken"),
    },
  };
  try {
    const command = new GetCredentialsForIdentityCommand(params);
    const response = await cognitoIdClient.send(command);

    // fix case for other AWS services auth
    response.Credentials.accessKeyId = response.Credentials.AccessKeyId;
    response.Credentials.secretAccessKey = response.Credentials.SecretKey;
    response.Credentials.sessionToken = response.Credentials.SessionToken;
    response.Credentials.expiration = response.Credentials.Expiration;

    sessionStorage.setItem("AWSCredentials", JSON.stringify(response));
    return response.Credentials;
  } catch (error) {
    console.error("Error getting credentials: ", error);
    throw error;
  }
};

export const getAWSCreds = async () => {
  let creds = {};
  try {
    creds.accessKeyId = sessionStorage.getItem("accessKeyId");
    creds.secretAccessKey = sessionStorage.getItem("secretAccessKey");
    creds.sessionToken = sessionStorage.getItem("sessionToken");
    creds.expiration = sessionStorage.getItem("expiration");
    creds.expiration = new Date(sessionStorage.getItem("expiration"));
    return creds;
  } catch (error) {
    throw error;
  }
};

export const refreshToken = async () => {
  const params = {
    AuthFlow: "REFRESH_TOKEN_AUTH",
    ClientId: awsConfig.COGNITO_CLIENT_ID,
    AuthParameters: {
      REFRESH_TOKEN: sessionStorage.getItem("refreshToken"),
    },
  };

  try {
    const command = new InitiateAuthCommand(params);
    const { AuthenticationResult } = await cognitoClient.send(command);
    if (AuthenticationResult) {
      sessionStorage.setItem("idToken", AuthenticationResult.IdToken || "");
      sessionStorage.setItem(
        "accessToken",
        AuthenticationResult.AccessToken || ""
      );
      await getIdentityId();
      await setAWSCreds();
      return true;
    }
  } catch (error) {
    throw error;
  }
};

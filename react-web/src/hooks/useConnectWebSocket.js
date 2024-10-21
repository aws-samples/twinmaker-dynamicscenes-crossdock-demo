import * as awsConfig from "../awsconfig";

//import * as AWS from "aws-sdk";
import { iot, mqtt } from "aws-iot-device-sdk-v2";
import { useEffect, useState } from "react";

export function useConnectWebSocket() {
  //const [wSconnection, setWSconnection] = useState();

  async function connectWebSocket() {
    try {
      // Create client ID for MQTT connection
      let credentials = JSON.parse(
        sessionStorage.getItem("AWSCredentials")
      ).Credentials;
      //credentials.expiration = new Date(credentials?.expiration);
      console.log("Websocket Credentials: ", credentials);
      let random = Math.floor(Math.random() * 1000000);
      let client_id = "dashboard_" + random;
      console.log("Connecting to websocket with client id: ", client_id);
      // LWT
      const lastWillMsg = JSON.parse('{ "client_id": "' + client_id + '" }');
      const lwt = new mqtt.MqttWill("/lost_connections", mqtt.QoS, lastWillMsg);

      let config =
        iot.AwsIotMqttConnectionConfigBuilder.new_builder_for_websocket()
          .with_clean_session(true)
          .with_client_id(client_id)
          .with_credentials(
            awsConfig.REGION,
            credentials.AccessKeyId,
            credentials.SecretKey,
            credentials.SessionToken
          )
          .with_endpoint(awsConfig.IOT_ENDPOINT)
          .with_will(lwt)
          .build();

      const client = new mqtt.MqttClient();

      const connection = client.new_connection(config);

      connection.on("connect", (session_present) => {
        console.log("Connected: session_present=", session_present);
        return connection;
      });

      connection.on("interrupt", (error) => {
        console.log(`Connection interrupted: error=${error}`);
      });
      connection.on("resume", (return_code, session_present) => {
        console.log(
          `Resumed: rc: ${return_code} existing session: ${session_present}`
        );
      });
      connection.on("disconnect", () => {
        console.log("Disconnected - websocket hook");
      });
      connection.on("error", (error) => {
        return error;
      });
      connection.connect();
      //setWSconnection(connection);
      return connection;
    } catch (e) {
      console.log("Error connecting to websocket: ", e);
    }
  }

  return { connectWebSocket };
}

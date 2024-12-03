import * as awsConfig from "../awsconfig";

import { iot, mqtt } from "aws-iot-device-sdk-v2";

export function useConnectWebSocket() {

  async function connectWebSocket() {
    try {
      // Create client ID for MQTT connection
      let credentials = JSON.parse(
        sessionStorage.getItem("AWSCredentials")
      );

      let random = Math.floor(Math.random() * 1000000);
      let client_id = "dashboard_" + random;

      // LWT
      const lastWillMsg = JSON.parse('{ "client_id": "' + client_id + '" }');
      const lwt = new mqtt.MqttWill("/lost_connections", mqtt.QoS, lastWillMsg);

      let config =
        iot.AwsIotMqttConnectionConfigBuilder.new_builder_for_websocket()
          .with_clean_session(true)
          .with_client_id(client_id)
          .with_credentials(
            awsConfig.REGION,
            credentials.accessKeyId,
            credentials.secretAccessKey,
            credentials.sessionToken
          )
          .with_endpoint(awsConfig.IOT_ENDPOINT)
          .with_will(lwt)
          .build();

      const client = new mqtt.MqttClient();

      const connection = client.new_connection(config);

      connection.on("connect", (session_present) => {
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
      connection.on("error", (error) => {
        return error;
      });
      connection.connect();
      //setWSconnection(connection);
      return connection;
    } catch (error) {
      throw error;
    }
  }

  return { connectWebSocket };
}

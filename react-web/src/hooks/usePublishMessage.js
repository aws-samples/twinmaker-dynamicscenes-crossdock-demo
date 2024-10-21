import { mqtt } from "aws-iot-device-sdk-v2";

export function usePublishMessage(mqttPayload) {
  function publishMessage() {
    try {
      if (
        mqttPayload?.current?.connection?.config &&
        mqttPayload?.current?.message
      ) {
        console.log(
          "2. Publishing message hook ",
          mqttPayload.current.message,
          " to topic ",
          mqttPayload.current.topic,
          " on connection ",
          mqttPayload.current.connection
        );
        mqttPayload.current.connection.publish(
          mqttPayload.current.topic,
          JSON.stringify(mqttPayload.current.message),
          mqtt.QoS.AtLeastOnce
        );
      }
    } catch (e) {
      console.log("Error publishing message: ", e);
    }
  }

  return { publishMessage };
}

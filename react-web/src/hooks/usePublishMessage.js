import { mqtt } from "aws-iot-device-sdk-v2";

export function usePublishMessage(mqttPayload) {
  function publishMessage() {
    try {
      if (
        mqttPayload?.current?.connection?.config &&
        mqttPayload?.current?.message
      ) {
        mqttPayload.current.connection.publish(
          mqttPayload.current.topic,
          JSON.stringify(mqttPayload.current.message),
          mqtt.QoS.AtLeastOnce
        );
      }
    } catch (error) {
      throw error;
    }
  }

  return { publishMessage };
}

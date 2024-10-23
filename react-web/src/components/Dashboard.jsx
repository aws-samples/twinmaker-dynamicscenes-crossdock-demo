import * as AWS from "aws-sdk";
import * as awsConfig from "../awsconfig";

import { useEffect, useRef, useState } from "react";

import Navbar from "./Navbar";
import TwinMaker from "./TwinMaker";
import { mqtt } from "aws-iot-device-sdk-v2";
import { refreshToken } from "../hooks/useCognitoAuthv3";
import { useConnectWebSocket } from "../hooks/useConnectWebSocket";
import { useNavigate } from "react-router-dom";

const Dashboard = () => {
  const navigate = useNavigate();
  const region = awsConfig.REGION;
  AWS.config.region = region;
  const connectionRef = useRef(null);
  const topics = useRef([]);

  // State
  const [dashboardConnected, setDashboardConnected] = useState(false);
  const [connection, setConnection] = useState(null);
  const { connectWebSocket } = useConnectWebSocket();

  let client_id = useRef(null);

  useEffect(() => {
    connectWebSocket().then((response) => {
      setConnection(response);
      connectionRef.current = response;
      client_id.current = response.config.client_id;
      console.log("Dashboard connection:", connectionRef);
      setDashboardConnected(true);
      setInterval(refreshToken, 3300000); // 3300000 for 55 mins
    });
  }, [setDashboardConnected]);

  const reconnectWebSocket = () => {
    connectWebSocket().then((response) => {
      connectionRef.current = response;
      setConnection(response);
      client_id.current = response.config.client_id;
      subscribeToTopics();
      console.log("Reconnected dashboard connection:", connectionRef);
      setDashboardConnected(true);
    });
  }

  const disconnectWebSocket = () => {
    unSubscribeFromTopics().then(() => {
      connectionRef.current.disconnect().then((response) => {
        console.log("Dashboard disconnected from MQTT broker: ", response);
        setDashboardConnected(false);
      });
    });
  }

  function logout() {
    console.log("Logout");
    navigate("/");
  }

  const subscribeToTopics = () => {
    topics.current.forEach((topic) => {
      try {
        console.log("Subscription Connection:", connectionRef.current);
        let sub = connectionRef.current.subscribe(
          topic,
          mqtt.QoS.AtLeastOnce,
          (topic, payload, dup, qos, retain) => {
            processMqttMessage(payload, topic);
          }
        );
        console.log("Subscribed to MQTT topic: ", sub);
      } catch (e) {
        console.log("Error subscribing to topic: ", e);
      }
    });
  }

  const unSubscribeFromTopics = async () => {
    topics.current.forEach((topic) => {
      try {
        console.log("Un-subscribe Connection:", connectionRef.current);
        connectionRef.current.unsubscribe(topic).then((response) => {
          console.log("Un-subscribed from MQTT topic: ", response);
        });
      } catch (e) {
        console.log("Error un-subscribing from topic: ", e);
      }
    });
  }

  const processMqttMessage = (msg, topic) => {
    const decoder = new TextDecoder("utf8");
    let message = JSON.parse(decoder.decode(new Uint8Array(msg)));
    console.log("Received MQTT message: ", message, " on topic: ", topic);
    if ("clientId" in message) {
      // do something?
    }
  }

  return (
    <div data-bs-theme="dark">
      <Navbar
        dashboardConnected={dashboardConnected}
        clientId={client_id.current}
        disconnect={disconnectWebSocket}
        reconnect={reconnectWebSocket}
        logout={logout}
      >
      </Navbar>
      <div className="container-fluid">
        <div className="row m-1">
          <TwinMaker />
        </div>
      </div>
    </div>
  );
}
export default Dashboard;

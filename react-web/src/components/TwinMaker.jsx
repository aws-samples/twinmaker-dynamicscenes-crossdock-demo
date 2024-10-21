import * as awsConfig from "../awsconfig";

import { TimeSync } from "@iot-app-kit/react-components";
import TwinMakerScene from "./TwinMakerScene";
import {
  useSceneComposerApi,
} from "@iot-app-kit/scene-composer";
import { useState } from "react";

const TwinMaker = () => {
  const [selectedEntityId, setSelectedEntityId] = useState([]);
  const [queryData, setQueryData] = useState(null);
  const composerApi = useSceneComposerApi(awsConfig.TWINMAKER_SCENE_ID);

  const onSelectionChanged = (selection) => {
    console.log("OnSelectionChanged: ", selection);
    try {
      if (
        selection.additionalComponentData &&
        selection.additionalComponentData[0]?.dataBindingContext?.entityId
      ) {
        const entityId =
          selection.additionalComponentData[0].dataBindingContext.entityId;
        if (selectedEntityId !== entityId) {
          let IQueryData = { entityId: entityId };
          setSelectedEntityId(entityId);
          setQueryData(IQueryData);
          console.log("IQueryData: ", IQueryData);
        }
      }
    } catch (e) {
      console.log("on selection changed error:", e);
    }
  }

  return (
    <TimeSync initialViewport={{ duration: "1m" }}>
      <div className="row">
        <div className="col-md-12">
          <TwinMakerScene
            onSelectionChanged={onSelectionChanged}
          />
        </div>
      </div>
      <div className="row">
        <div className="col-md-12">

        </div>
      </div>

    </TimeSync>
  );
}

export default TwinMaker;

import "@cloudscape-design/global-styles/index.css";
import "/node_modules/@iot-app-kit/components/styles.css";
import "./SceneViewer.scss";

import * as awsConfig from "../awsconfig";

import {
  Density,
  Mode,
  applyDensity,
  applyMode,
} from "@cloudscape-design/global-styles";
import { useEffect, useMemo, useState } from "react";

import { COMPOSER_FEATURES } from "@iot-app-kit/scene-composer";
import { SceneViewer as SceneViewerComp } from "@iot-app-kit/scene-composer";
import { getEntityQuery } from "../hooks/useTwinMakerQuery";
import { initialize } from "@iot-app-kit/source-iottwinmaker";

function TwinMakerScene({ onSelectionChanged }) {
  const [palletEntities, setPalletEntities] = useState([])
  applyDensity(Density.Comfortable);
  applyMode(Mode.Dark);

  useEffect(() => {
    getEntityQuery().then((response) => {
      setPalletEntities(response);
    });

  },[]);

  const workSpace = awsConfig.TWINMAKER_WORKSPACE;
  const sceneId = awsConfig.TWINMAKER_SCENE_ID;

  let credentials = JSON.parse(
    sessionStorage.getItem("AWSCredentials")
  ).Credentials;
  credentials.expiration = new Date(credentials.expiration);
  const dataSource = initialize(workSpace, {
    awsCredentials: credentials,
    awsRegion: awsConfig.REGION,
  });

  const sceneLoader = useMemo(
    () => dataSource?.s3SceneLoader(sceneId),
    [dataSource, sceneId]
  );
  const sceneMetadataModule = useMemo(
    () => dataSource.sceneMetadataModule(sceneId),
    [dataSource,sceneId]
  );

  const componentTypeQueries = useMemo(() => [], []);

  const entityQueries = useMemo(() => palletEntities, [palletEntities]);

  const queries = useMemo(
    () => [
      ...componentTypeQueries.map((q) => dataSource.query.timeSeriesData(q)),
      ...entityQueries.map((q) => dataSource.query.timeSeriesData(q)),
    ],
    [dataSource, componentTypeQueries, entityQueries]
  );

  function onWidgetClick(widget) {}

  return (
    <div className="col col-md-12">
      <div className="card shadow mb-4 d-flex align-items-stretch">
        <div className="card-header text-white">
          <div className="row">
            <div className="col">
              <h4>Cross-dock Indoor Location Tracking</h4>
            </div>
          </div>
        </div>
        <div className="card-body">
          <div className="row">
            <div className="col overflow-hidden">
              <div className="SceneViewer">
                <SceneViewerComp
                  sceneLoader={sceneLoader}
                  config={{
                    dracoDecoder: {
                      enable: true,
                      path: "https://www.gstatic.com/draco/versioned/decoders/1.5.3/", // path to the draco files
                    },
                      featureConfig: {
                        [COMPOSER_FEATURES.DynamicScene]: true
                      }
                  }}
                  onSelectionChanged={onSelectionChanged}
                  sceneMetadataModule={sceneMetadataModule}
                  onWidgetClick={onWidgetClick}
                  queries={queries}
                  sceneComposerId={sceneId}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TwinMakerScene;

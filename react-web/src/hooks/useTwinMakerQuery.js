import * as awsConfig from "../awsconfig";

import { IoTTwinMakerClient, ListEntitiesCommand } from "@aws-sdk/client-iottwinmaker";

const getPalletEntities = async () => {
    let credentials = JSON.parse(
        sessionStorage.getItem("AWSCredentials")
      ).Credentials;
    credentials.expiration = new Date(credentials.expiration);
    
    const TwinMaker = new IoTTwinMakerClient({ region: awsConfig.REGION, credentials: credentials });
    const workspaceId = awsConfig.TWINMAKER_WORKSPACE;
    const filter = [ {
        componentTypeId: awsConfig.PALLET_COMPONENT_TYPE_ID
    }];
    const params = {
        workspaceId: workspaceId,
        maxResults: 100,
        filters: filter
    };
    return await TwinMaker.send(new ListEntitiesCommand(params));
}

export const getEntityQuery = async () => {
    // get entities from TwinMaker and create entityQueries array of objects
    const palletEntities = await getPalletEntities().then((response) => {
        // extract the entity ID from the entity summaries
        const entityIds = response.entitySummaries.map((entity) => entity.entityId);
        const entityQueries = entityIds.map((entityId) => {
            return {
                entityId: entityId,
                componentName: "sitewiseBase",
                properties: [
                    { propertyName: awsConfig.DWELLTIME_PROPERTY_ID }
                ],
            }
        });
        return entityQueries;
    });
    return palletEntities;
};
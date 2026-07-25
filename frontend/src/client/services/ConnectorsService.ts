/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ConnectorCreate } from '../models/ConnectorCreate';
import type { ConnectorUpdate } from '../models/ConnectorUpdate';
import type { SyncConfig } from '../models/SyncConfig';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ConnectorsService {
    /**
     * List Connectors
     * @returns any Successful Response
     * @throws ApiError
     */
    public static listConnectorsApiV1ConnectorsGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/connectors/',
        });
    }
    /**
     * Create Connector
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static createConnectorApiV1ConnectorsPost(
        requestBody: ConnectorCreate,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/connectors/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Connector
     * @param connectorId
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static updateConnectorApiV1ConnectorsConnectorIdPut(
        connectorId: string,
        requestBody: ConnectorUpdate,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/connectors/{connector_id}',
            path: {
                'connector_id': connectorId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Handle Webhook
     * Ingress point for all external webhooks (e.g. from GitHub, Slack).
     * @param source
     * @returns any Successful Response
     * @throws ApiError
     */
    public static handleWebhookApiV1ConnectorsWebhooksSourcePost(
        source: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/connectors/webhooks/{source}',
            path: {
                'source': source,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Schedule Sync
     * Endpoint for the Sync Dashboard to configure polling intervals.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static scheduleSyncApiV1ConnectorsSchedulePost(
        requestBody: SyncConfig,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/connectors/schedule',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Dashboard Metrics
     * Returns metrics for the Sync Dashboard.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getDashboardMetricsApiV1ConnectorsDashboardGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/connectors/dashboard',
        });
    }
}

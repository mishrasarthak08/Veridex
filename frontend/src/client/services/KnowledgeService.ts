/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { RetrieveRequest } from '../models/RetrieveRequest';
import type { SyncRequest } from '../models/SyncRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class KnowledgeService {
    /**
     * Trigger Sync
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static triggerSyncApiV1KnowledgeSyncPost(
        requestBody: SyncRequest,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/knowledge/sync',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Retrieve Knowledge
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static retrieveKnowledgeApiV1KnowledgeRetrievePost(
        requestBody: RetrieveRequest,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/knowledge/retrieve',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Graph Data
     * Fetches the Knowledge Graph structure (nodes and edges) for UI visualization.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getGraphDataApiV1KnowledgeGraphGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/knowledge/graph',
        });
    }
}

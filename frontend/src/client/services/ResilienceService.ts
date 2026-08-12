/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChaosRequest } from '../models/ChaosRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ResilienceService {
    /**
     * Stream Chaos
     * Server-Sent Events for chaos logs
     * @returns any Successful Response
     * @throws ApiError
     */
    public static streamChaosApiV1ResilienceChaosStreamGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/resilience/chaos/stream',
        });
    }
    /**
     * Start Chaos
     * Start specific chaos injection
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static startChaosApiV1ResilienceChaosPost(
        requestBody: ChaosRequest,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/resilience/chaos',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}

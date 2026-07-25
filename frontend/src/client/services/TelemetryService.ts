/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class TelemetryService {
    /**
     * Get Telemetry Logs
     * Retrieve recent AI telemetry logs.
     * Currently only accessible to system admins.
     * @param skip
     * @param limit
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getTelemetryLogsApiV1TelemetryGet(
        skip?: number,
        limit: number = 50,
    ): CancelablePromise<Array<Record<string, any>>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/telemetry/',
            query: {
                'skip': skip,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}

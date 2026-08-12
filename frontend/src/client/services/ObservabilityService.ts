/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ObservabilityService {
    /**
     * Get Traces
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getTracesApiV1ObservabilityTracesGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/observability/traces',
        });
    }
    /**
     * Get Trace
     * Returns the AI execution trace for the Playground UI.
     * @param traceId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getTraceApiV1ObservabilityTracesTraceIdGet(
        traceId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/observability/traces/{trace_id}',
            path: {
                'trace_id': traceId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Generate Synthetic Data
     * @param count
     * @returns any Successful Response
     * @throws ApiError
     */
    public static generateSyntheticDataApiV1ObservabilitySyntheticGeneratePost(
        count: number = 10,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/observability/synthetic/generate',
            query: {
                'count': count,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Cost Analytics
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getCostAnalyticsApiV1ObservabilityMetricsCostGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/observability/metrics/cost',
        });
    }
}

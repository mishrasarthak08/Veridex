/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class HealthService {
    /**
     * Health Check
     * @returns any Successful Response
     * @throws ApiError
     */
    public static healthCheckApiV1HealthHealthGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/health/health',
        });
    }
    /**
     * Readiness Check
     * @returns any Successful Response
     * @throws ApiError
     */
    public static readinessCheckApiV1HealthReadyGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/health/ready',
        });
    }
    /**
     * Liveness Check
     * @returns any Successful Response
     * @throws ApiError
     */
    public static livenessCheckApiV1HealthLiveGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/health/live',
        });
    }
}

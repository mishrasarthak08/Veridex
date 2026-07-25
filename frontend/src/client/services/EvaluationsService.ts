/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class EvaluationsService {
    /**
     * List Evaluations
     * List historical evaluation runs.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static listEvaluationsApiV1EvaluationsGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/evaluations/',
        });
    }
    /**
     * Trigger Evaluation
     * Trigger a new evaluation run.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static triggerEvaluationApiV1EvaluationsRunPost(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/evaluations/run',
        });
    }
}

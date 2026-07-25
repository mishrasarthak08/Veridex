/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ApprovalDecision } from '../models/ApprovalDecision';
import type { GoalRequest } from '../models/GoalRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AgentsService {
    /**
     * Submit Goal
     * Submits a complex goal to the Orchestrator, which breaks it into a DAG
     * and schedules it across multiple specialized agents.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static submitGoalApiV1AgentsGoalPost(
        requestBody: GoalRequest,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/agents/goal',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Submit Approval
     * Endpoint for a human to approve or reject a pending sensitive action.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static submitApprovalApiV1AgentsApprovePost(
        requestBody: ApprovalDecision,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/agents/approve',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Execution Timeline
     * SSE Endpoint for streaming the Execution Timeline UI in real-time.
     * Listens to the 'system_events' channel on the AgentBus.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static executionTimelineApiV1AgentsTimelineGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/agents/timeline',
        });
    }
}

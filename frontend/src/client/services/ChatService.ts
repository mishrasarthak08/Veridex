/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChatMessageCreate } from '../models/ChatMessageCreate';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ChatService {
    /**
     * Chat Status
     * @returns any Successful Response
     * @throws ApiError
     */
    public static chatStatusApiV1ChatGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/chat/',
        });
    }
    /**
     * Get Chat Threads
     * Retrieve all unique chat threads for the current user, ordered by most recently updated.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getChatThreadsApiV1ChatThreadsGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/chat/threads',
        });
    }
    /**
     * Get Chat History
     * Retrieve chat history for a specific thread_id.
     * @param threadId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getChatHistoryApiV1ChatHistoryThreadIdGet(
        threadId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/chat/history/{thread_id}',
            path: {
                'thread_id': threadId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Add Chat Message
     * Save a new chat message to history.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static addChatMessageApiV1ChatMessagePost(
        requestBody: ChatMessageCreate,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/chat/message',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Chat Stream
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static chatStreamApiV1ChatStreamPost(
        requestBody: ChatMessageCreate,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/chat/stream',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}

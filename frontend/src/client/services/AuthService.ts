/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_login_access_token_api_v1_auth_login_post } from '../models/Body_login_access_token_api_v1_auth_login_post';
import type { MFAVerifyRequest } from '../models/MFAVerifyRequest';
import type { UserCreate } from '../models/UserCreate';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AuthService {
    /**
     * Register User
     * Register a new user.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static registerUserApiV1AuthRegisterPost(
        requestBody: UserCreate,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/register',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Login Access Token
     * OAuth2 compatible token login, get an access token for future requests.
     * @param formData
     * @returns any Successful Response
     * @throws ApiError
     */
    public static loginAccessTokenApiV1AuthLoginPost(
        formData: Body_login_access_token_api_v1_auth_login_post,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/login',
            formData: formData,
            mediaType: 'application/x-www-form-urlencoded',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Read Users Me
     * Get current user profile.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static readUsersMeApiV1AuthMeGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/auth/me',
        });
    }
    /**
     * Github Login
     * Redirects to GitHub OAuth authorize URL.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static githubLoginApiV1AuthGithubLoginGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/auth/github/login',
        });
    }
    /**
     * Github Callback
     * Exchanges code for access token, fetches user data, and issues JWT.
     * @param code
     * @returns any Successful Response
     * @throws ApiError
     */
    public static githubCallbackApiV1AuthGithubCallbackGet(
        code: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/auth/github/callback',
            query: {
                'code': code,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Google Login
     * Redirects to Google OAuth authorize URL.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static googleLoginApiV1AuthGoogleLoginGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/auth/google/login',
        });
    }
    /**
     * Google Callback
     * Exchanges code for Google access and refresh tokens, fetches user data, and issues JWT.
     * @param code
     * @returns any Successful Response
     * @throws ApiError
     */
    public static googleCallbackApiV1AuthGoogleCallbackGet(
        code: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/auth/google/callback',
            query: {
                'code': code,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Refresh Access Token
     * Refresh access token for current user using HttpOnly cookie.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static refreshAccessTokenApiV1AuthRefreshPost(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/refresh',
        });
    }
    /**
     * Mfa Setup
     * Generate MFA secret and URI for setup.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static mfaSetupApiV1AuthMfaSetupPost(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/mfa/setup',
        });
    }
    /**
     * Mfa Verify
     * Verify MFA code and enable MFA or issue full tokens if already enabled.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static mfaVerifyApiV1AuthMfaVerifyPost(
        requestBody: MFAVerifyRequest,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/mfa/verify',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Logout
     * Logout current user.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static logoutApiV1AuthLogoutPost(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/logout',
        });
    }
}

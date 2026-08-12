/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PermissionAssign } from '../models/PermissionAssign';
import type { RoleCreate } from '../models/RoleCreate';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class GovernanceService {
    /**
     * Governance Status
     * @returns any Successful Response
     * @throws ApiError
     */
    public static governanceStatusApiV1GovernanceGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/governance/',
        });
    }
    /**
     * Get Policies
     * Return all roles with their associated permissions.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getPoliciesApiV1GovernancePoliciesGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/governance/policies',
        });
    }
    /**
     * Get Roles
     * List all available roles and their permissions.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getRolesApiV1GovernanceRolesGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/governance/roles',
        });
    }
    /**
     * Create Role
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static createRoleApiV1GovernanceRolesPost(
        requestBody: RoleCreate,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/governance/roles',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Role Permissions
     * @param roleId
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static updateRolePermissionsApiV1GovernanceRolesRoleIdPermissionsPut(
        roleId: string,
        requestBody: Array<PermissionAssign>,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/governance/roles/{role_id}/permissions',
            path: {
                'role_id': roleId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Assign Role To User
     * @param userId
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static assignRoleToUserApiV1GovernanceUsersUserIdRolesPost(
        userId: string,
        requestBody: Array<string>,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/governance/users/{user_id}/roles',
            path: {
                'user_id': userId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Simulate Policy
     * Simulate a policy decision.
     * @param resource
     * @param action
     * @param userId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static simulatePolicyApiV1GovernanceSimulatePost(
        resource: string,
        action: string,
        userId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/governance/simulate',
            query: {
                'resource': resource,
                'action': action,
                'user_id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Audit Log
     * Returns the immutable audit log.
     * @param limit
     * @param actor
     * @param resource
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getAuditLogApiV1GovernanceAuditLogGet(
        limit: number = 50,
        actor?: string,
        resource?: string,
    ): CancelablePromise<Array<Record<string, any>>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/governance/audit-log',
            query: {
                'limit': limit,
                'actor': actor,
                'resource': resource,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}

/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class GovernanceService {
    /**
     * Get Audit Log
     * Returns the immutable audit log for the compliance dashboard.
     * (Mocked response for now)
     * @param tenantId
     * @param limit
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getAuditLogApiV1GovernanceAuditLogGet(
        tenantId: string,
        limit: number = 50,
    ): CancelablePromise<Array<Record<string, any>>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/governance/audit-log',
            query: {
                'tenant_id': tenantId,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Tenant Quotas
     * Returns the usage vs quota limits for the given tenant.
     * @param tenantId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getTenantQuotasApiV1GovernanceQuotasGet(
        tenantId: string,
    ): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/governance/quotas',
            query: {
                'tenant_id': tenantId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}

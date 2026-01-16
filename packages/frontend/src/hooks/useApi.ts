/**
 * React Query hooks for API data fetching.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type {
    Opportunity,
    OpportunityFilters,
    PaginatedResponse,
    PropertyAnalysis,
    IngestionRequest,
    IngestionResponse,
    SystemStatus,
} from "@/types";

// Query keys for cache management
export const queryKeys = {
    opportunities: (filters: OpportunityFilters) => ["opportunities", filters] as const,
    property: (uprn: string) => ["property", uprn] as const,
    systemStatus: () => ["systemStatus"] as const,
};

/**
 * Fetch paginated opportunities by postcode district.
 */
export function useOpportunities(filters: OpportunityFilters) {
    return useQuery({
        queryKey: queryKeys.opportunities(filters),
        queryFn: async () => {
            const params = new URLSearchParams();
            params.set("postcode_district", filters.postcode_district);
            if (filters.min_discount_pct) params.set("min_discount_pct", String(filters.min_discount_pct));
            if (filters.max_price) params.set("max_price", String(filters.max_price));
            if (filters.sort_by) params.set("sort_by", filters.sort_by);
            if (filters.page) params.set("page", String(filters.page));
            if (filters.per_page) params.set("per_page", String(filters.per_page));
            if (filters.property_types?.length) {
                filters.property_types.forEach(type => params.append("property_types", type));
            }

            const response = await api.get<PaginatedResponse<Opportunity>>(
                `/api/v1/opportunities?${params.toString()}`
            );
            return response.data;
        },
        enabled: !!filters.postcode_district && filters.postcode_district.length >= 2,
    });
}

/**
 * Fetch detailed analysis for a single property.
 */
export function usePropertyAnalysis(uprn: string) {
    return useQuery({
        queryKey: queryKeys.property(uprn),
        queryFn: async () => {
            const response = await api.get<PropertyAnalysis>(
                `/api/v1/properties/${uprn}/analysis`
            );
            return response.data;
        },
        enabled: !!uprn,
    });
}

/**
 * Trigger data ingestion.
 */
export function useIngestion() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async (request: IngestionRequest) => {
            const response = await api.post<IngestionResponse>(
                "/api/v1/system/ingest",
                request
            );
            return response.data;
        },
        onSuccess: () => {
            // Invalidate opportunities cache after ingestion
            queryClient.invalidateQueries({ queryKey: ["opportunities"] });
        },
    });
}

/**
 * Fetch system status.
 */
export function useSystemStatus() {
    return useQuery({
        queryKey: queryKeys.systemStatus(),
        queryFn: async () => {
            const response = await api.get<SystemStatus>("/api/v1/system/status");
            return response.data;
        },
        refetchInterval: 30000, // Refresh every 30 seconds
    });
}

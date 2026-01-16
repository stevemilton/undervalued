/**
 * TypeScript types for API responses and data models.
 */

export interface Address {
    paon?: string;
    saon?: string;
    street: string;
    town: string;
    postcode: string;
}

export interface Listing {
    listing_id: string;
    external_url: string;
    asking_price: number;
    listing_date: string;
    agent_name?: string;
    source: string;
}

export interface Metrics {
    current_ppsf: number;
    market_ppsf_12m?: number;
    undervalued_index?: number;
    projected_yield?: number;
    comparable_count: number;
    priority?: "High" | "Medium" | "Low";
    calculated_at: string;
}

export interface Opportunity {
    uprn: string;
    address: Address;
    property_type: string;
    floor_area_sqft?: number;
    epc_rating?: string;
    listing: Listing;
    metrics: Metrics;
}

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    per_page: number;
    pages: number;
}

export interface Transaction {
    transaction_id: string;
    uprn: string;
    price_paid: number;
    date_of_transfer: string;
    transaction_category: string;
    price_per_sqft?: number;
    floor_area_sqft?: number;
}

export interface PropertyAnalysis {
    property: {
        uprn: string;
        address_bs7666: Address;
        floor_area_sqft?: number;
        property_type: string;
        epc_rating?: string;
        current_listing_id?: string;
    };
    current_listing?: Listing;
    metrics?: Metrics;
    historical_transactions: Transaction[];
    comparables: Transaction[];
    chart_data: {
        scatter_plot: Array<{
            x: string;
            y: number;
            label: string;
            is_subject: boolean;
        }>;
    };
}

export interface OpportunityFilters {
    postcode_district: string;
    min_discount_pct?: number;
    max_price?: number;
    property_types?: string[];
    sort_by?: string;
    page?: number;
    per_page?: number;
}

export interface IngestionRequest {
    source?: string;
    postcode_districts?: string[];
    force_refresh?: boolean;
}

export interface IngestionResponse {
    task_id: string;
    status: string;
    estimated_completion: string;
}

export interface SystemStatus {
    database: string;
    redis: string;
    last_ingestion?: string;
    total_properties: number;
    total_opportunities: number;
}

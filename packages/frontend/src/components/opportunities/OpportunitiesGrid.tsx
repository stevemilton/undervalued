"use client";

import type { Opportunity, PaginatedResponse } from "@/types";
import { OpportunityCard } from "./OpportunityCard";

interface OpportunitiesGridProps {
    data?: PaginatedResponse<Opportunity>;
    isLoading: boolean;
    isError: boolean;
    onPageChange: (page: number) => void;
}

export function OpportunitiesGrid({
    data,
    isLoading,
    isError,
    onPageChange,
}: OpportunitiesGridProps) {
    if (isLoading) {
        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {Array.from({ length: 6 }).map((_, i) => (
                    <div
                        key={i}
                        className="h-64 bg-slate-800/50 rounded-2xl animate-pulse"
                    />
                ))}
            </div>
        );
    }

    if (isError) {
        return (
            <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-8 text-center">
                <p className="text-red-400 font-semibold mb-2">Failed to load opportunities</p>
                <p className="text-slate-400 text-sm">
                    Please check that the backend API is running on port 8000.
                </p>
            </div>
        );
    }

    if (!data || data.items.length === 0) {
        return (
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-12 text-center">
                <div className="text-6xl mb-4">🏠</div>
                <h3 className="text-xl font-semibold text-white mb-2">
                    No Opportunities Found
                </h3>
                <p className="text-slate-400">
                    Try searching a different postcode district or adjusting your filters.
                </p>
            </div>
        );
    }

    return (
        <div>
            {/* Results Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {data.items.map((opportunity) => (
                    <OpportunityCard key={opportunity.uprn} opportunity={opportunity} />
                ))}
            </div>

            {/* Pagination */}
            {data.pages > 1 && (
                <div className="flex items-center justify-center gap-2 mt-8">
                    <button
                        onClick={() => onPageChange(data.page - 1)}
                        disabled={data.page <= 1}
                        className="px-4 py-2 bg-slate-800 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-700 transition-colors"
                    >
                        Previous
                    </button>

                    <div className="flex items-center gap-1">
                        {Array.from({ length: Math.min(data.pages, 5) }).map((_, i) => {
                            const pageNum = i + 1;
                            return (
                                <button
                                    key={pageNum}
                                    onClick={() => onPageChange(pageNum)}
                                    className={`w-10 h-10 rounded-lg font-semibold transition-colors ${pageNum === data.page
                                            ? "bg-blue-500 text-white"
                                            : "bg-slate-800 text-slate-400 hover:bg-slate-700"
                                        }`}
                                >
                                    {pageNum}
                                </button>
                            );
                        })}
                        {data.pages > 5 && (
                            <span className="px-2 text-slate-500">...</span>
                        )}
                    </div>

                    <button
                        onClick={() => onPageChange(data.page + 1)}
                        disabled={data.page >= data.pages}
                        className="px-4 py-2 bg-slate-800 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-700 transition-colors"
                    >
                        Next
                    </button>
                </div>
            )}

            {/* Results Summary */}
            <p className="text-center text-sm text-slate-500 mt-4">
                Showing {data.items.length} of {data.total} opportunities
            </p>
        </div>
    );
}

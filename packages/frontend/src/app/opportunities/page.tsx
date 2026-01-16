"use client";

import { useState } from "react";
import Link from "next/link";
import { useOpportunities } from "@/hooks/useApi";
import { OpportunitiesGrid } from "@/components/opportunities/OpportunitiesGrid";
import { SearchFilters } from "@/components/opportunities/SearchFilters";

export default function OpportunitiesPage() {
    const [filters, setFilters] = useState({
        postcode_district: "",
        min_discount_pct: undefined as number | undefined,
        max_price: undefined as number | undefined,
        property_types: undefined as string[] | undefined,
        page: 1,
        per_page: 12,
    });

    const { data, isLoading, isError } = useOpportunities(filters);

    const handleSearch = (newFilters: {
        postcode_district: string;
        min_discount_pct?: number;
        max_price?: number;
        property_types?: string[];
    }) => {
        setFilters({
            ...newFilters,
            page: 1,
            per_page: 12,
        });
    };

    const handlePageChange = (page: number) => {
        setFilters((prev) => ({ ...prev, page }));
        window.scrollTo({ top: 0, behavior: "smooth" });
    };

    return (
        <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
            {/* Header */}
            <header className="border-b border-slate-700/50 backdrop-blur-lg bg-slate-900/50 sticky top-0 z-50">
                <div className="container mx-auto px-4 py-4 flex items-center justify-between">
                    <Link href="/" className="text-2xl font-bold text-white">
                        Undervalued
                    </Link>
                    <nav className="flex gap-6">
                        <Link href="/opportunities" className="text-blue-400 font-medium">
                            Opportunities
                        </Link>
                        <Link href="/admin" className="text-slate-400 hover:text-white transition-colors">
                            Admin
                        </Link>
                    </nav>
                </div>
            </header>

            <div className="container mx-auto px-4 py-8">
                {/* Page Title */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">Property Opportunities</h1>
                    <p className="text-slate-400">
                        Find undervalued properties in your target area using PPSF analysis
                    </p>
                </div>

                {/* Search Filters */}
                <div className="mb-8">
                    <SearchFilters onSearch={handleSearch} isLoading={isLoading} />
                </div>

                {/* Results */}
                {filters.postcode_district ? (
                    <OpportunitiesGrid
                        data={data}
                        isLoading={isLoading}
                        isError={isError}
                        onPageChange={handlePageChange}
                    />
                ) : (
                    <div className="bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700/50 p-12 text-center">
                        <div className="text-6xl mb-4">🔍</div>
                        <h2 className="text-xl font-semibold text-white mb-2">
                            Enter a Postcode to Start
                        </h2>
                        <p className="text-slate-400 max-w-md mx-auto">
                            Search for undervalued properties by postcode district.
                            We&apos;ll show you opportunities ranked by how much they&apos;re below market value.
                        </p>
                    </div>
                )}
            </div>
        </main>
    );
}

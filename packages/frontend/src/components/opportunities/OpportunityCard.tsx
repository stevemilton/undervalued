"use client";

import Link from "next/link";
import type { Opportunity } from "@/types";
import { formatCurrency, formatPercent } from "@/lib/utils";

interface OpportunityCardProps {
    opportunity: Opportunity;
}

export function OpportunityCard({ opportunity }: OpportunityCardProps) {
    const { address, listing, metrics } = opportunity;

    // Format address for display
    const displayAddress = [
        address.saon,
        address.paon,
        address.street,
    ].filter(Boolean).join(" ");

    // Determine priority badge color
    const priorityColors = {
        High: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
        Medium: "bg-amber-500/20 text-amber-400 border-amber-500/30",
        Low: "bg-slate-500/20 text-slate-400 border-slate-500/30",
    };
    const priorityColor = priorityColors[metrics.priority || "Low"];

    return (
        <Link
            href={`/properties/${opportunity.uprn}`}
            className="group block bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700/50 p-6 hover:border-blue-500/50 transition-all hover:shadow-lg hover:shadow-blue-500/10"
        >
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
                <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-semibold text-white truncate group-hover:text-blue-400 transition-colors">
                        {displayAddress}
                    </h3>
                    <p className="text-sm text-slate-400">
                        {address.town}, {address.postcode}
                    </p>
                </div>
                {metrics.priority && (
                    <span className={`px-3 py-1 text-xs font-semibold rounded-full border ${priorityColor}`}>
                        {metrics.priority}
                    </span>
                )}
            </div>

            {/* Price Row */}
            <div className="flex items-baseline gap-3 mb-4">
                <span className="text-2xl font-bold text-white">
                    {formatCurrency(listing.asking_price)}
                </span>
                {metrics.undervalued_index !== undefined && metrics.undervalued_index > 0 && (
                    <span className="text-emerald-400 font-semibold">
                        {formatPercent(metrics.undervalued_index)} below market
                    </span>
                )}
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-3 gap-4 p-4 bg-slate-900/50 rounded-xl">
                <div className="text-center">
                    <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">PPSF</p>
                    <p className="text-lg font-semibold text-white">
                        £{Math.round(metrics.current_ppsf)}
                    </p>
                </div>
                <div className="text-center border-x border-slate-700">
                    <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Market</p>
                    <p className="text-lg font-semibold text-slate-300">
                        {metrics.market_ppsf_12m ? `£${Math.round(metrics.market_ppsf_12m)}` : "—"}
                    </p>
                </div>
                <div className="text-center">
                    <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Yield</p>
                    <p className="text-lg font-semibold text-blue-400">
                        {metrics.projected_yield ? formatPercent(metrics.projected_yield) : "—"}
                    </p>
                </div>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-700/50">
                <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-500">{opportunity.property_type}</span>
                    {opportunity.floor_area_sqft && (
                        <>
                            <span className="text-slate-600">•</span>
                            <span className="text-xs text-slate-500">
                                {Math.round(opportunity.floor_area_sqft)} sqft
                            </span>
                        </>
                    )}
                    {opportunity.epc_rating && (
                        <>
                            <span className="text-slate-600">•</span>
                            <span className="text-xs text-slate-500">EPC {opportunity.epc_rating}</span>
                        </>
                    )}
                </div>
                <span className="text-xs text-slate-500">
                    {metrics.comparable_count} comps
                </span>
            </div>
        </Link>
    );
}

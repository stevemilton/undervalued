"use client";

import { use } from "react";
import Link from "next/link";
import { usePropertyAnalysis } from "@/hooks/useApi";
import { formatCurrency, formatPercent } from "@/lib/utils";
import type { Transaction } from "@/types";

interface PropertyPageProps {
    params: Promise<{ uprn: string }>;
}

export default function PropertyPage({ params }: PropertyPageProps) {
    const resolvedParams = use(params);
    const { data, isLoading, isError } = usePropertyAnalysis(resolvedParams.uprn);

    if (isLoading) {
        return (
            <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
                <Header />
                <div className="container mx-auto px-4 py-8">
                    <div className="animate-pulse space-y-6">
                        <div className="h-12 bg-slate-800 rounded-xl w-1/2" />
                        <div className="h-64 bg-slate-800 rounded-xl" />
                        <div className="h-40 bg-slate-800 rounded-xl" />
                    </div>
                </div>
            </main>
        );
    }

    if (isError || !data) {
        return (
            <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
                <Header />
                <div className="container mx-auto px-4 py-8">
                    <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-8 text-center">
                        <h2 className="text-xl font-semibold text-red-400 mb-2">Property Not Found</h2>
                        <p className="text-slate-400">
                            The property with UPRN {resolvedParams.uprn} could not be found.
                        </p>
                        <Link
                            href="/opportunities"
                            className="mt-4 inline-block px-6 py-3 bg-slate-700 text-white rounded-xl hover:bg-slate-600"
                        >
                            Back to Search
                        </Link>
                    </div>
                </div>
            </main>
        );
    }

    const { property, current_listing, metrics, historical_transactions } = data;
    const address = property.address_bs7666;
    const displayAddress = [address.saon, address.paon, address.street].filter(Boolean).join(" ");

    return (
        <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
            <Header />

            <div className="container mx-auto px-4 py-8">
                {/* Breadcrumb */}
                <nav className="mb-6 text-sm">
                    <Link href="/opportunities" className="text-slate-400 hover:text-white">
                        Opportunities
                    </Link>
                    <span className="text-slate-600 mx-2">/</span>
                    <span className="text-slate-300">{property.uprn}</span>
                </nav>

                {/* Property Header */}
                <div className="mb-8">
                    <div className="flex items-start justify-between mb-4">
                        <div>
                            <h1 className="text-3xl font-bold text-white mb-2">{displayAddress}</h1>
                            <p className="text-slate-400">{address.town}, {address.postcode}</p>
                        </div>
                        {metrics?.priority && (
                            <span className={`px-4 py-2 text-sm font-semibold rounded-full ${metrics.priority === "High"
                                    ? "bg-emerald-500/20 text-emerald-400"
                                    : metrics.priority === "Medium"
                                        ? "bg-amber-500/20 text-amber-400"
                                        : "bg-slate-500/20 text-slate-400"
                                }`}>
                                {metrics.priority} Priority
                            </span>
                        )}
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Main Content */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Key Metrics */}
                        <div className="bg-slate-800/50 rounded-2xl border border-slate-700/50 p-6">
                            <h2 className="text-lg font-semibold text-white mb-4">Valuation Analysis</h2>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <MetricBox
                                    label="Asking PPSF"
                                    value={`£${Math.round(metrics?.current_ppsf || 0)}`}
                                />
                                <MetricBox
                                    label="Market PPSF"
                                    value={metrics?.market_ppsf_12m ? `£${Math.round(metrics.market_ppsf_12m)}` : "—"}
                                    subtext="12-month avg"
                                />
                                <MetricBox
                                    label="Discount"
                                    value={metrics?.undervalued_index ? formatPercent(metrics.undervalued_index) : "—"}
                                    highlight={metrics?.undervalued_index && metrics.undervalued_index > 0.1}
                                />
                                <MetricBox
                                    label="Est. Yield"
                                    value={metrics?.projected_yield ? formatPercent(metrics.projected_yield) : "—"}
                                />
                            </div>
                        </div>

                        {/* Transaction History */}
                        <div className="bg-slate-800/50 rounded-2xl border border-slate-700/50 p-6">
                            <h2 className="text-lg font-semibold text-white mb-4">Transaction History</h2>
                            {historical_transactions.length > 0 ? (
                                <div className="space-y-3">
                                    {historical_transactions.map((tx: Transaction) => (
                                        <div
                                            key={tx.transaction_id}
                                            className="flex items-center justify-between py-3 border-b border-slate-700/50 last:border-0"
                                        >
                                            <div>
                                                <p className="text-white font-medium">{formatCurrency(tx.price_paid)}</p>
                                                <p className="text-sm text-slate-400">
                                                    {new Date(tx.date_of_transfer).toLocaleDateString("en-GB", {
                                                        year: "numeric",
                                                        month: "short",
                                                        day: "numeric",
                                                    })}
                                                </p>
                                            </div>
                                            {tx.price_per_sqft && (
                                                <span className="text-slate-300">
                                                    £{Math.round(tx.price_per_sqft)}/sqft
                                                </span>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-slate-400">No transaction history available.</p>
                            )}
                        </div>
                    </div>

                    {/* Sidebar */}
                    <div className="space-y-6">
                        {/* Listing Info */}
                        {current_listing && (
                            <div className="bg-slate-800/50 rounded-2xl border border-slate-700/50 p-6">
                                <h2 className="text-lg font-semibold text-white mb-4">Current Listing</h2>
                                <p className="text-3xl font-bold text-white mb-2">
                                    {formatCurrency(current_listing.asking_price)}
                                </p>
                                <p className="text-slate-400 text-sm mb-4">
                                    Listed {new Date(current_listing.listing_date).toLocaleDateString("en-GB")}
                                </p>
                                {current_listing.agent_name && (
                                    <p className="text-sm text-slate-400 mb-4">
                                        via {current_listing.agent_name}
                                    </p>
                                )}
                                <a
                                    href={current_listing.external_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="block w-full px-4 py-3 bg-blue-500 text-white font-semibold rounded-xl text-center hover:bg-blue-600 transition-colors"
                                >
                                    View on {current_listing.source}
                                </a>
                            </div>
                        )}

                        {/* Property Details */}
                        <div className="bg-slate-800/50 rounded-2xl border border-slate-700/50 p-6">
                            <h2 className="text-lg font-semibold text-white mb-4">Property Details</h2>
                            <dl className="space-y-3">
                                <DetailRow label="Type" value={property.property_type} />
                                <DetailRow
                                    label="Floor Area"
                                    value={property.floor_area_sqft ? `${Math.round(property.floor_area_sqft)} sqft` : "—"}
                                />
                                <DetailRow label="EPC Rating" value={property.epc_rating || "—"} />
                                <DetailRow label="UPRN" value={property.uprn} />
                                <DetailRow label="Comparables" value={`${metrics?.comparable_count || 0} used`} />
                            </dl>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}

function Header() {
    return (
        <header className="border-b border-slate-700/50 backdrop-blur-lg bg-slate-900/50 sticky top-0 z-50">
            <div className="container mx-auto px-4 py-4 flex items-center justify-between">
                <Link href="/" className="text-2xl font-bold text-white">
                    Undervalued
                </Link>
                <nav className="flex gap-6">
                    <Link href="/opportunities" className="text-slate-400 hover:text-white transition-colors">
                        Opportunities
                    </Link>
                    <Link href="/admin" className="text-slate-400 hover:text-white transition-colors">
                        Admin
                    </Link>
                </nav>
            </div>
        </header>
    );
}

function MetricBox({
    label,
    value,
    subtext,
    highlight,
}: {
    label: string;
    value: string;
    subtext?: string;
    highlight?: boolean;
}) {
    return (
        <div className="p-4 bg-slate-900/50 rounded-xl text-center">
            <p className="text-xs text-slate-500 uppercase tracking-wider mb-2">{label}</p>
            <p className={`text-2xl font-bold ${highlight ? "text-emerald-400" : "text-white"}`}>
                {value}
            </p>
            {subtext && <p className="text-xs text-slate-500 mt-1">{subtext}</p>}
        </div>
    );
}

function DetailRow({ label, value }: { label: string; value: string }) {
    return (
        <div className="flex justify-between py-2 border-b border-slate-700/50 last:border-0">
            <dt className="text-slate-400">{label}</dt>
            <dd className="text-white font-medium">{value}</dd>
        </div>
    );
}

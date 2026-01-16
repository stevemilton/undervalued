"use client";

import { useSystemStatus, useIngestion } from "@/hooks/useApi";
import { useState } from "react";
import Link from "next/link";

export default function AdminPage() {
    const { data: status, isLoading } = useSystemStatus();
    const ingestion = useIngestion();
    const [postcodeDistricts, setPostcodeDistricts] = useState("");

    const handleIngest = () => {
        const districts = postcodeDistricts
            .split(",")
            .map((d) => d.trim().toUpperCase())
            .filter(Boolean);

        ingestion.mutate({
            source: "all",
            postcode_districts: districts.length > 0 ? districts : undefined,
            force_refresh: false,
        });
    };

    return (
        <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
            {/* Header */}
            <header className="border-b border-slate-700/50 backdrop-blur-lg bg-slate-900/50">
                <div className="container mx-auto px-4 py-4 flex items-center justify-between">
                    <Link href="/" className="text-2xl font-bold text-white">
                        Undervalued
                    </Link>
                    <nav className="flex gap-6">
                        <Link href="/opportunities" className="text-slate-400 hover:text-white transition-colors">
                            Opportunities
                        </Link>
                        <Link href="/admin" className="text-blue-400 font-medium">
                            Admin
                        </Link>
                    </nav>
                </div>
            </header>

            <div className="container mx-auto px-4 py-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">Admin Dashboard</h1>
                    <p className="text-slate-400">
                        Manage data ingestion and monitor system health
                    </p>
                </div>

                <div className="grid gap-6 md:grid-cols-2">
                    {/* Data Ingestion */}
                    <div className="bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700/50 p-6">
                        <h2 className="text-xl font-semibold text-white mb-4">Data Ingestion</h2>
                        <p className="text-slate-400 text-sm mb-4">
                            Trigger data refresh from Land Registry and property portals.
                        </p>

                        <div className="mb-4">
                            <label className="block text-sm font-medium text-slate-300 mb-2">
                                Postcode Districts (comma-separated)
                            </label>
                            <input
                                type="text"
                                placeholder="e.g., SW15, W14, SE1"
                                value={postcodeDistricts}
                                onChange={(e) => setPostcodeDistricts(e.target.value)}
                                className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                            <p className="text-xs text-slate-500 mt-1">
                                Leave empty to process all districts
                            </p>
                        </div>

                        <button
                            onClick={handleIngest}
                            disabled={ingestion.isPending}
                            className="w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-emerald-500 text-white font-semibold rounded-xl hover:opacity-90 transition-opacity disabled:opacity-50"
                        >
                            {ingestion.isPending ? "Starting..." : "Trigger Ingestion"}
                        </button>

                        {ingestion.isSuccess && (
                            <div className="mt-4 p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl">
                                <p className="text-emerald-400 font-medium">Ingestion Started</p>
                                <p className="text-sm text-slate-400">
                                    Task ID: {ingestion.data?.task_id}
                                </p>
                            </div>
                        )}

                        {ingestion.isError && (
                            <div className="mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
                                <p className="text-red-400 font-medium">Ingestion Failed</p>
                                <p className="text-sm text-slate-400">
                                    Check that the backend API is running.
                                </p>
                            </div>
                        )}
                    </div>

                    {/* System Status */}
                    <div className="bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700/50 p-6">
                        <h2 className="text-xl font-semibold text-white mb-4">System Status</h2>

                        {isLoading ? (
                            <div className="space-y-3">
                                {[1, 2, 3, 4].map((i) => (
                                    <div key={i} className="h-10 bg-slate-700 rounded animate-pulse" />
                                ))}
                            </div>
                        ) : (
                            <div className="space-y-4">
                                <StatusRow
                                    label="Database"
                                    status={status?.database || "unknown"}
                                />
                                <StatusRow
                                    label="Redis"
                                    status={status?.redis || "unknown"}
                                />
                                <StatusRow
                                    label="Total Properties"
                                    value={status?.total_properties?.toString() || "0"}
                                />
                                <StatusRow
                                    label="Active Opportunities"
                                    value={status?.total_opportunities?.toString() || "0"}
                                />
                                {status?.last_ingestion && (
                                    <StatusRow
                                        label="Last Ingestion"
                                        value={new Date(status.last_ingestion).toLocaleString()}
                                    />
                                )}
                            </div>
                        )}
                    </div>

                    {/* Quick Actions */}
                    <div className="bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700/50 p-6">
                        <h2 className="text-xl font-semibold text-white mb-4">Quick Actions</h2>
                        <div className="space-y-3">
                            <a
                                href="http://localhost:8000/docs"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="block w-full px-4 py-3 bg-slate-700 text-white rounded-xl hover:bg-slate-600 transition-colors text-center"
                            >
                                Open API Documentation
                            </a>
                            <a
                                href="http://localhost:8000/health"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="block w-full px-4 py-3 bg-slate-700 text-white rounded-xl hover:bg-slate-600 transition-colors text-center"
                            >
                                Check Health Endpoint
                            </a>
                        </div>
                    </div>

                    {/* API Info */}
                    <div className="bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700/50 p-6">
                        <h2 className="text-xl font-semibold text-white mb-4">API Endpoints</h2>
                        <div className="space-y-2 font-mono text-sm">
                            <p className="text-slate-400">
                                <span className="text-emerald-400">GET</span>{" "}
                                /api/v1/opportunities
                            </p>
                            <p className="text-slate-400">
                                <span className="text-emerald-400">GET</span>{" "}
                                /api/v1/properties/{"{uprn}"}/analysis
                            </p>
                            <p className="text-slate-400">
                                <span className="text-amber-400">POST</span>{" "}
                                /api/v1/system/ingest
                            </p>
                            <p className="text-slate-400">
                                <span className="text-emerald-400">GET</span>{" "}
                                /api/v1/system/status
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}

function StatusRow({
    label,
    status,
    value,
}: {
    label: string;
    status?: string;
    value?: string;
}) {
    const getStatusColor = (s: string) => {
        if (s === "connected" || s === "healthy") {
            return "bg-emerald-500/20 text-emerald-400";
        } else if (s === "disconnected" || s === "unhealthy") {
            return "bg-red-500/20 text-red-400";
        }
        return "bg-slate-600/50 text-slate-400";
    };

    return (
        <div className="flex justify-between items-center py-2 border-b border-slate-700/50 last:border-0">
            <span className="text-slate-400">{label}</span>
            {value ? (
                <span className="text-white font-medium">{value}</span>
            ) : (
                <span className={`px-3 py-1 rounded-full text-sm ${getStatusColor(status || "unknown")}`}>
                    {status || "Unknown"}
                </span>
            )}
        </div>
    );
}

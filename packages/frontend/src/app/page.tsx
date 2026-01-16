import Link from "next/link";

export default function Home() {
    return (
        <main className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
            <div className="container mx-auto px-4 py-16">
                {/* Hero Section */}
                <div className="text-center mb-16">
                    <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
                        Undervalued
                    </h1>
                    <p className="text-xl md:text-2xl text-slate-300 max-w-3xl mx-auto">
                        UK Property Opportunity Finder - Identify undervalued properties using
                        HM Land Registry data and advanced PPSF analysis.
                    </p>
                </div>

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto mb-16">
                    <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                        <div className="text-4xl font-bold text-emerald-400 mb-2">90%+</div>
                        <div className="text-slate-300">UPRN Matching Accuracy</div>
                    </div>
                    <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                        <div className="text-4xl font-bold text-blue-400 mb-2">&lt;24h</div>
                        <div className="text-slate-300">Data Freshness</div>
                    </div>
                    <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                        <div className="text-4xl font-bold text-purple-400 mb-2">&lt;200ms</div>
                        <div className="text-slate-300">API Response Time</div>
                    </div>
                </div>

                {/* CTA Buttons */}
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <Link
                        href="/opportunities"
                        className="px-8 py-4 bg-gradient-to-r from-blue-500 to-emerald-500 text-white font-semibold rounded-xl hover:opacity-90 transition-opacity text-center"
                    >
                        View Opportunities
                    </Link>
                    <Link
                        href="/admin"
                        className="px-8 py-4 bg-white/10 backdrop-blur text-white font-semibold rounded-xl border border-white/20 hover:bg-white/20 transition-colors text-center"
                    >
                        Admin Dashboard
                    </Link>
                </div>

                {/* Feature List */}
                <div className="mt-24 max-w-4xl mx-auto">
                    <h2 className="text-3xl font-bold text-white text-center mb-12">
                        How It Works
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="flex gap-4">
                            <div className="flex-shrink-0 w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center">
                                <span className="text-2xl">📊</span>
                            </div>
                            <div>
                                <h3 className="text-xl font-semibold text-white mb-2">PPSF Analysis</h3>
                                <p className="text-slate-400">
                                    Compare asking price per square foot against local market benchmarks.
                                </p>
                            </div>
                        </div>
                        <div className="flex gap-4">
                            <div className="flex-shrink-0 w-12 h-12 bg-emerald-500/20 rounded-xl flex items-center justify-center">
                                <span className="text-2xl">🏠</span>
                            </div>
                            <div>
                                <h3 className="text-xl font-semibold text-white mb-2">Land Registry Data</h3>
                                <p className="text-slate-400">
                                    Real historical transaction data from HM Land Registry.
                                </p>
                            </div>
                        </div>
                        <div className="flex gap-4">
                            <div className="flex-shrink-0 w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center">
                                <span className="text-2xl">🎯</span>
                            </div>
                            <div>
                                <h3 className="text-xl font-semibold text-white mb-2">Opportunity Scoring</h3>
                                <p className="text-slate-400">
                                    Properties ranked by undervalued index for quick decision making.
                                </p>
                            </div>
                        </div>
                        <div className="flex gap-4">
                            <div className="flex-shrink-0 w-12 h-12 bg-amber-500/20 rounded-xl flex items-center justify-center">
                                <span className="text-2xl">📍</span>
                            </div>
                            <div>
                                <h3 className="text-xl font-semibold text-white mb-2">Postcode Filtering</h3>
                                <p className="text-slate-400">
                                    Search by postcode district to find opportunities in your target areas.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}

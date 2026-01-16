"use client";

import { useState } from "react";

interface SearchFiltersProps {
    onSearch: (filters: {
        postcode_district: string;
        min_discount_pct?: number;
        max_price?: number;
        property_types?: string[];
    }) => void;
    isLoading?: boolean;
}

const PROPERTY_TYPES = ["Detached", "Semi-Detached", "Terraced", "Flat"];

export function SearchFilters({ onSearch, isLoading }: SearchFiltersProps) {
    const [postcodeDistrict, setPostcodeDistrict] = useState("");
    const [minDiscount, setMinDiscount] = useState<string>("");
    const [maxPrice, setMaxPrice] = useState<string>("");
    const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
    const [showAdvanced, setShowAdvanced] = useState(false);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSearch({
            postcode_district: postcodeDistrict.toUpperCase(),
            min_discount_pct: minDiscount ? parseFloat(minDiscount) / 100 : undefined,
            max_price: maxPrice ? parseFloat(maxPrice) : undefined,
            property_types: selectedTypes.length > 0 ? selectedTypes : undefined,
        });
    };

    const togglePropertyType = (type: string) => {
        setSelectedTypes((prev) =>
            prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
        );
    };

    return (
        <form onSubmit={handleSubmit} className="bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700/50 p-6">
            {/* Main Search Row */}
            <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                    <label htmlFor="postcode" className="block text-sm font-medium text-slate-300 mb-2">
                        Postcode District
                    </label>
                    <input
                        id="postcode"
                        type="text"
                        placeholder="e.g., SW15, W14, SE1"
                        value={postcodeDistrict}
                        onChange={(e) => setPostcodeDistrict(e.target.value.toUpperCase())}
                        className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        required
                    />
                </div>
                <div className="flex items-end gap-2">
                    <button
                        type="submit"
                        disabled={isLoading || !postcodeDistrict}
                        className="px-6 py-3 bg-gradient-to-r from-blue-500 to-emerald-500 text-white font-semibold rounded-xl hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isLoading ? "Searching..." : "Search"}
                    </button>
                    <button
                        type="button"
                        onClick={() => setShowAdvanced(!showAdvanced)}
                        className="px-4 py-3 bg-slate-700 text-slate-300 rounded-xl hover:bg-slate-600 transition-colors"
                    >
                        {showAdvanced ? "Less" : "More"}
                    </button>
                </div>
            </div>

            {/* Advanced Filters */}
            {showAdvanced && (
                <div className="mt-6 pt-6 border-t border-slate-700">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                        <div>
                            <label htmlFor="minDiscount" className="block text-sm font-medium text-slate-300 mb-2">
                                Min Discount (%)
                            </label>
                            <input
                                id="minDiscount"
                                type="number"
                                min="0"
                                max="50"
                                placeholder="e.g., 10"
                                value={minDiscount}
                                onChange={(e) => setMinDiscount(e.target.value)}
                                className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                        <div>
                            <label htmlFor="maxPrice" className="block text-sm font-medium text-slate-300 mb-2">
                                Max Price (£)
                            </label>
                            <input
                                id="maxPrice"
                                type="number"
                                min="0"
                                step="10000"
                                placeholder="e.g., 500000"
                                value={maxPrice}
                                onChange={(e) => setMaxPrice(e.target.value)}
                                className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                    </div>

                    <div>
                        <p className="text-sm font-medium text-slate-300 mb-3">Property Types</p>
                        <div className="flex flex-wrap gap-2">
                            {PROPERTY_TYPES.map((type) => (
                                <button
                                    key={type}
                                    type="button"
                                    onClick={() => togglePropertyType(type)}
                                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${selectedTypes.includes(type)
                                            ? "bg-blue-500 text-white"
                                            : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                                        }`}
                                >
                                    {type}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </form>
    );
}

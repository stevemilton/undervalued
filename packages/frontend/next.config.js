/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,

    // Enable standalone output for Docker deployments
    output: 'standalone',

    // Environment variables exposed to the browser
    env: {
        NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    },

    // Image optimization domains
    images: {
        domains: [],
    },

    // Disable x-powered-by header
    poweredByHeader: false,
};

module.exports = nextConfig;

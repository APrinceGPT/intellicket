import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Turbopack configuration
  turbopack: {
    rules: {
      '*.svg': {
        loaders: ['@svgr/webpack'],
        as: '*.js',
      },
    },
  },
  
  // Configure static file serving
  images: {
    domains: ['localhost'],
    unoptimized: true, // For development
  },
  
  // API route configuration
  async rewrites() {
    return [
      {
        source: '/api/csdai/:path*',
        destination: '/api/csdai/:path*',
      },
    ];
  },
};

export default nextConfig;

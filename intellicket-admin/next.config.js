/** @type {import('next').NextConfig} */
const nextConfig = {
  // Turbopack configuration for Next.js 15
  turbopack: {
    root: __dirname,
  },
  
  // Admin interface specific configuration
  env: {
    ADMIN_PORT: '3001',
    BACKEND_URL: 'http://localhost:5003',
    FRONTEND_URL: 'http://localhost:3000',
  },
  
  // API routes configuration
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET, POST, PUT, DELETE, OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'Content-Type, Authorization' },
        ],
      },
    ]
  },


}

module.exports = nextConfig
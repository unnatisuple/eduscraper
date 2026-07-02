import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    domains: ['fonts.googleapis.com', 'fonts.gstatic.com'],
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
        ],
      },
    ];
  },
};

export default nextConfig;

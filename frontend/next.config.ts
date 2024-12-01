/** @type {import('next').NextConfig} */


const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "example.com", // Replace with your domain
        pathname: "/images/**", // Adjust path to your image structure
      },
    ],
  },
};

module.exports = nextConfig;

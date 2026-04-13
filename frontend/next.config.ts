import type { NextConfig } from 'next';

const config: NextConfig = {
  output: 'standalone',
  typescript: { ignoreBuildErrors: true },
  eslint: { ignoreDuringBuilds: true },
  webpack: (config, { isServer }) => {
    if (!isServer) {
      // plotly.js source has dynamic require() patterns that break webpack.
      // Use the pre-built UMD dist instead — it's already bundled and safe.
      // '$' = exact-match only. Without it webpack does prefix-match and
      // breaks sub-path imports like 'plotly.js/dist/plotly' used by react-plotly.js.
      config.resolve.alias = {
        ...config.resolve.alias,
        'plotly.js$': 'plotly.js/dist/plotly.min.js',
        'plotly.js/dist/plotly$': 'plotly.js/dist/plotly.min.js',
      };
    }
    return config;
  },
};

export default config;

import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        rappi: {
          orange:      '#FF441B',
          'orange-dk': '#E03516',
          'orange-lt': '#FF6B35',
          'orange-bg': '#FFF4F1',
        },
      },
      typography: () => ({
        DEFAULT: {
          css: {
            maxWidth: 'none',
            color: '#374151',
            'h1,h2,h3,h4': { color: '#111827' },
            a: { color: '#FF441B', textDecoration: 'none', '&:hover': { textDecoration: 'underline' } },
            code: {
              backgroundColor: '#F3F4F6',
              padding: '1px 5px',
              borderRadius: '4px',
              fontWeight: '400',
              fontSize: '0.85em',
            },
            'code::before': { content: '""' },
            'code::after':  { content: '""' },
            table:        { fontSize: '0.8125rem', marginTop: '0.75rem', marginBottom: '0.75rem' },
            'thead th':   { color: '#FF441B', fontWeight: '600', padding: '8px 12px' },
            'tbody td':   { padding: '6px 12px' },
            'tbody tr:hover td': { backgroundColor: '#FFF9F7' },
          },
        },
      }),
    },
  },
  plugins: [require('@tailwindcss/typography')],
};

export default config;

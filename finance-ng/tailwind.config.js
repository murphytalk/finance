module.exports = {
  future: {
    removeDeprecatedGapUtilities: true,
    purgeLayersByDefault: true,
  },
  purge: ['./src/**/*.html', './src/**/*.ts'],
  theme: {
    extend: {},
    container: {
      center: true,
      padding: "15px",
    },
  },
  variants: {},
  plugins: [],
  important: true,
}

module.exports = {
  prefix: 'tw-',
  purge: ['./src/**/*.{html,ts}'],
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {},
    container: {
      center: true,
      padding: "15px",
    },
  },
  variants: {
    extend: {},
  },
  plugins: [],
  important: true,
};

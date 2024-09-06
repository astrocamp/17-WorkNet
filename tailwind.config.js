/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./**/*.{html,js}"],
  theme: {
    data: {
      active: 'active~="true"',
      disabled: 'disabled~="true"',
    },
    extend: {},
  },
  plugins: [],
};

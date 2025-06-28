/**  Tailwind Config — Versión Final 1
 *   (sin corePlugins extra; listo para compilar sin errores)
 *   @type {import('tailwindcss').Config}
 */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html", // templates de cualquier app Django
    "./**/*.py",                // clases embebidas en vistas o serializers
  ],

  theme: {
    fontFamily: {
      sans: ['Inter', 'ui-sans-serif', 'system-ui'],
    },
    extend: {
      colors: {
        /* ---- Marca ---- */
        brand:      '#E5525F',
        brandDark:  '#D04450',
        brandLight: '#F9E7E9',

        /* ---- Fondo gris global ---- */
        wash: '#F5F6F7',
      },
      borderRadius: {
        lg: '0.5rem',
      },
    },
  },

  plugins: [
    require('@tailwindcss/forms'),
    // agrega aquí otros plugins cuando los necesites
  ],
};

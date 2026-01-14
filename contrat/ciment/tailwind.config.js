/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './templates/**/*.html',
        './contracts/templates/**/*.html',
        './dashboard/templates/**/*.html',
        './evaluations/templates/**/*.html',
        './orders/templates/**/*.html',
        './reports/templates/**/*.html',
        './suppliers/templates/**/*.html',
        './users/templates/**/*.html',
        './static/js/**/*.js'
    ],
    theme: {
        extend: {}
    },
    plugins: []
};

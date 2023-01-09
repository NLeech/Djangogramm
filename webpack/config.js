const path = require("path");
const webpack = require("webpack")
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = [
    {
        entry: "./src/js/index.js",
        output: {
            filename: "index.js",
            path: path.resolve(__dirname, "../djangogramm/djangogramm/static/js")
        },
        module: {
            rules: [
                {
                    test: /\.(scss)$/,
                    use: [MiniCssExtractPlugin.loader, "css-loader", "sass-loader"],
                },
                {
                    test: /\.(css)$/,
                    use: [MiniCssExtractPlugin.loader, "css-loader"],
                },
            ],
        },
        plugins: [
            new MiniCssExtractPlugin({filename: "../css/index.css"}),
            new webpack.ProvidePlugin({$: 'jquery',jQuery: 'jquery',})
        ],
        mode: "development",
    },
];


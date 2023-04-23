const path = require('path');

module.exports = {
    // 指定入口文件
    entry: './src/index.js',

    // 指定输出文件和路径
    output: {
        filename: 'main.js',
        path: path.resolve(__dirname, 'dist'),
    },

    // 配置模块解析规则
    module: {
        rules: [
            {
                // 针对 JavaScript 文件应用 Babel 转译
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env'],
                    },
                },
            },

            {
                test: /\.css$/i,
                use: ['style-loader', 'css-loader'],
            },
        ],
    },

    // 设定模式，可选值有 'production' 和 'development'，'production' 会进行代码压缩，'development' 不会
    mode: 'development',
};

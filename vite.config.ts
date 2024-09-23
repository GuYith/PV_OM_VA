import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import Icons from 'unplugin-icons/vite'
import IconsResolver from 'unplugin-icons/resolver'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import Inspect from 'vite-plugin-inspect'
import path, { resolve } from 'path'

// import * as buffer from 'buffer'

const pathSrc = path.resolve(__dirname, 'src')
// https://vitejs.dev/config/
export default defineConfig({
    define: {
        'process.env': process.env,
        // buffer: buffer.Buffer,
    },
    resolve: {
        alias: [
            {
                find: '@',
                replacement: resolve(__dirname, './src'),
            },
        ],
    },
    plugins: [
        vue(),
        AutoImport({
            // Auto import functions from Vue, e.g. ref, reactive, toRef...
            // 自动导入 Vue 相关函数，如：ref, reactive, toRef 等
            imports: ['vue'],

            // Auto import functions from Element Plus, e.g. ElMessage, ElMessageBox... (with style)
            // 自动导入 Element Plus 相关函数，如：ElMessage, ElMessageBox... (带样式)
            resolvers: [
                ElementPlusResolver(),

                // Auto import icon components
                // 自动导入图标组件
                IconsResolver({
                    prefix: 'Icon',
                }),
            ],
            dts: path.resolve(pathSrc, 'auto-imports.d.ts'),
        }),

        Components({
            resolvers: [
                // Auto register icon components
                // 自动注册图标组件
                IconsResolver({
                    enabledCollections: ['ep', 'mdi', 'ant-design'],
                }),
                // Auto register Element Plus components
                // 自动导入 Element Plus 组件
                ElementPlusResolver(),
            ],

            dts: path.resolve(pathSrc, 'components.d.ts'),
        }),

        Icons({
            autoInstall: true,
        }),

        Inspect(),
    ],
    //conference https://github.com/whidy/elementplus-tailwindcss-best-practice
    build: {
        rollupOptions: {
            output: {
                manualChunks(id: any) {
                    // 更新日期：2022年06月09日
                    // 下面这三行css代码打包的配置可以随你移除或者保留~移除后会自动生成一个css，和下面的示例图会有区别。
                    if (id.includes('assets/style.css')) {
                        return 'tailwindcss'
                    }
                    if (id.includes('element-plus/theme-chalk/')) {
                        // 当然也可以优化下这个判断，不过目前这样写足矣了。
                        return 'element-plus'
                    }
                },
            },
        },
    },

    server: {
        host: 'localhost',
        port: 5173,
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:8000/',
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api/, ''),
            },
        },
    },
})

import { resolve } from "path";

export default defineNuxtConfig({
  devtools: { enabled: false },
  runtimeConfig: {
    public: {
      baseURL: process.env.BASE_URL || 'http://localhost:8000',
    },
  },
  alias: {
    '@': resolve(__dirname, '/'),
    assets: "/<rootDir>/assets",
  },
  css: [
    "~/assets/styles/main.scss"
  ],
  modules: [
    '@element-plus/nuxt'
  ],
  elementPlus: {
    importStyle: 'scss',
  },
  vite: {
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: '@use "~/assets/styles/element/index.scss" as element;'
        }
      }
    }
  }
})

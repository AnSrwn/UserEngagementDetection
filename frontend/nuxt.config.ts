import { resolve } from "path";

export default defineNuxtConfig({
  devtools: { enabled: true },
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

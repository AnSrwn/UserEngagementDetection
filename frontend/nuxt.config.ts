import { resolve } from "path";

export default defineNuxtConfig({
  devtools: { enabled: false },
  runtimeConfig: {
    public: {
      baseUrl: '', // is overwritten by env variable NUXT_PUBLIC_BASE_URL
      stunServerUrl: '', // is overwritten by env variable NUXT_PUBLIC_STUN_SERVER_URL
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
    '@element-plus/nuxt',
    '@nuxtjs/i18n',
  ],
  elementPlus: {
    importStyle: 'scss',
  },
  i18n: {
    vueI18n: './i18n.config.ts',
    lazy: true,
    langDir: 'locales',
    strategy: "no_prefix",
    locales: [
        {
          code: 'en',
          name: 'English',
          file: 'en.json'
        },
      {
        code: 'de',
        name: 'Deutsch',
        file: 'de.json'
      }
    ],
    defaultLocale: 'en',
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

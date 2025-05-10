// docs/.vitepress/config.js
import { defineConfig } from 'vitepress'
export default defineConfig({
  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/./icon.svg' }],
    ['meta', { name: 'theme-color', content: '#ff7e17' }],
    ['meta', { property: 'og:title', content: "Nexios" }],
    ['meta', { property: 'og:description', content: "Nexios - Async web framework for Python" }],
    ['meta', { property: 'og:image', content: "./icon.svg" }],
    ['meta', { property: 'og:type', content: 'website' }],
    // ['meta', { property: 'og:url', content: docsLink }],
    // ['meta', { property: 'twitter:card', content: 'summary_large_image' }],
    // ['meta', { property: 'twitter:image', content: ogImage }],


]
,
  title: 'Nexios',
  description: 'Async web framework for Python',
  themeConfig: {
    logo: '/icon.svg',
    favicon: '/icon.svg',
    themeSwitcher: true,
    search:{
      provider: 'local'
    },
    nav: [
      { text: 'Architecture', link: '/architecture/async-python' },
      { text: 'Guide', link: '/guide/getting-started' },
      { text: "Howto's", link: '/howtos/index' },
      { text : "Websockets", link: "/websockets/index" },
      { text: 'API Reference', link: '/guide/api-reference' },
      { text: "Team", link: 'team' },
      { text: 'GitHub', link: 'https://github.com/nexios-labs/Nexios' }
    ],
    sidebar: {
      '/architecture/': [
        {
          text: 'Architecture',
          items: [
            { text: 'Async Python', link: '/architecture/async-python' },
            { text: 'Asgi', link: '/architecture/asgi' },
          ]
        }
      ],
      '/guide/': [
        {
          text: 'Guide',
          items: [
            { text: 'Getting Started', link: '/guide/getting-started' },
            { text: "CLI", link: "/guide/cli" },
            { text: "philosophy", link: "/guide/philosophy" },
            {
              items : [
            { text: 'Routing', link: '/guide/routing' },
            { text: 'Handlers', link: '/guide/handlers' },
            { text: 'Startups and Shutdowns', link: '/guide/startups-and-shutdowns' },
            { text: 'Request Inputs', link: '/guide/request-inputs' },
            { text: 'Configuration', link: '/guide/configuration' },
            { text: 'Sending Responses', link: '/guide/sending-responses' },
            { text : "Routers and subapps", link: "/guide/routers-and-subapps" },
            { text : "Middleware", link: "/guide/middleware" },
            { text : "Cookies", link: "/guide/cookies" },
            { text : "Headers", link: "/guide/headers" },
            { text : "Sessions", link: "/guide/sessions" },
            { text : "Request Info", link: "/guide/request-info" },
            { text : "Error Handling", link: "/guide/error-handling" },
            { text : "Pagination", link: "/guide/pagination" },
            { text : "Authentication", link: "/guide/authentication" },
            { text : "Class Based Hndlers", link: "/guide/class-based-handlers" },
            { text : "Events", link: "/guide/events" },
            { text : "Dependency Injection", link: "/guide/dependency-injection" },
            { text : "Static Files", link: "/guide/static-files" },



            { text: 'API Reference', link: '/guide/api-reference' },
              ]
            }
          ]
        }
      ],
      '/howtos/': [
        {
          text: 'Howto',
          items: [
            { text: 'Index', link: '/howtos/index' },
            { text : "File Upload", link: "/howtos/file-upload" },
            { text : "Templating", link: "/howtos/templating" },
            { text : "Orm Integration", link: "/howtos/orm-integration" },
            { text : "Static Files", link: "/howtos/static-files" },
            { text : "Websockets", link: "/howtos/websockets" },
            { text : "Health Checks", link: "/howtos/health-checks" },
            { text : "Caching", link: "/howtos/caching" },

          ]
        }
      ],
      "websockets": [
        {
          text: 'Websockets',
          items: [
            { text : "Websockets", link: "/websockets/index" },
            { text : "Channels", link: "/websockets/channels" },
            { text : "Groups", link: "/websockets/groups" },
            { text :"Events", link: "/websockets/events" },
            { text : "Consumer", link: "/websockets/consumer" },


          ]
        }
      ]
    }
  },
  markdown: {
    lineNumbers: true
  }
})

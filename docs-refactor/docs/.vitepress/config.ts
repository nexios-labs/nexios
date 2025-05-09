// docs/.vitepress/config.js

export default {
  head: [
    ['link', { rel: 'stylesheet', href: 'https://unpkg.com/tailwindcss@3.2.4/dist/tailwind.min.css' }],
    ['link', { rel: 'stylesheet', href: 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css' }],
    ['link', { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap' }],
    ['script', { src: 'https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4' }]


]
,
  title: 'Nexios',
  description: 'Async web framework for Python',
  themeConfig: {
    logo: '/icon.svg',
    nav: [
      { text: 'Architecture', link: '/architecture/async-python' },
      { text: 'Guide', link: '/guide/getting-started' },
      { text: "Howto's", link: '/howtos/index' },
      { text : "Websockets", link: "/howtos/websockets" },
      { text: 'API Reference', link: '/guide/api-reference' },
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



            { text: 'API Reference', link: '/guide/api-reference' },
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
          ]
        }
      ]
    }
  },
  markdown: {
    lineNumbers: true
  }
}

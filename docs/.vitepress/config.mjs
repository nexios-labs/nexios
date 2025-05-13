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
    socialLinks : [
      {icon : "github", link : "https://github.com/nexios-labs/nexios"},
      {icon : "twitter", link : "https://twitter.com/nexioslabs"},

    ],
    siteTitle: 'Nexios',
    logo: '/icon.svg',
    favicon: '/icon.svg',
    themeSwitcher: true,
    search:{
      provider: 'local'
    },
    nav: [
      { text: 'Guide', link: '/guide/getting-started' },
      { text : "Websockets", link: "/websockets/index" },
      { text : "OpenAPI", link: "/openapi/index" },
      { text: 'API Reference', link: '/api/application' },
      { text: "Team", link: 'team' },
    ],
    sidebar: {
     
      text: 'Architecture',
      items: [
        { text: 'Async Python', link: '/architecture/async-python' },
        { text: 'Asgi', link: '/architecture/asgi' },
      ],
        
    
      '/guide/': [
        {
          text: '',
          items: [
            
            { text: "CLI", link: "/guide/cli" },
            { text: 'Getting Started', link: '/guide/getting-started' },
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



            { text: 'File Upload', link: '/guide/file-upload' },
            { text: 'Cors', link: '/guide/cors' },
              ]
            }
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
      ],
      "openapi": [
        {
          text: 'OpenAPI',
          items: [
            { text: 'Index', link: '/openapi/index' },
            { text: 'Documenting Response Models with Pydantic', link: '/openapi/response-models' },
            { text: 'Request Schemas', link: '/openapi/request-schemas' },
            { text: "Request Parameters", link: "/openapi/request-parameters" },
            { text: 'Customizing OpenAPI Configuration', link: '/openapi/customizing-openapi-configuration' },
            { text: 'Authentication Documentation', link: '/openapi/authentication-documentation' },
          ]
        }
      ],
      "api": [
        {
          text: 'API Reference',
          items: [
            { text: 'Index', link: '/api/application' },
            { text: 'Routing', link: '/api/routing' },
            { text: "Response", link: "/api/response" },
            { text : "Exceptions", link : "/api/exceptions" },
            { text : "Websocket", link : "/api/websockets" },

          ]
        }
      ]
    }
  },

  markdown: {
    lineNumbers: true
  },
  ignoreDeadLinks: true
})

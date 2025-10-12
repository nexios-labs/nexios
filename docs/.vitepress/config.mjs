import { defineConfig } from 'vitepress'

export default defineConfig({
  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/./logo.png' }],
    ['meta', { name: 'theme-color', content: '#ff7e17' }],
    ['meta', { property: 'og:title', content: "Nexios - Python Web Framework" }],
    ['meta', { property: 'og:description', content: "Nexios is a modern, fast, and secure web framework for Python. It is designed to be easy to use and understand, while also being powerful and flexible." }],
    ['meta', { property: 'og:image', content: "/./logo.png" }],
    ['meta', { property: 'og:type', content: 'website' }],
  ],
  
  
  title: 'Nexios',
  base: "/nexios/",
  description: 'Nexios is a modern, fast, and secure web framework for Python. It is designed to be easy to use and understand, while also being powerful and flexible.',

  themeConfig: {
    siteTitle: 'Nexios',
    logo: '/logo.png',
    favicon: '/logo.png',
    themeSwitcher: true,

    socialLinks: [
      { icon: "github", link: "https://github.com/nexios-labs/nexios" },
      { icon: "twitter", link: "https://twitter.com/nexioslabs" },
    ],

    search: {
      provider: 'local'
    },

    nav: [
      { text: 'Intro', link: '/intro' },
      { text: 'Guide', link: '/guide/getting-started' },
      { text: 'Examples', link: '/api-examples' },
      { text : "Community", link:"/community"},
      { text: "Discussions", link:"https://github.com/orgs/nexios-labs/discussions"},
      { text: 'Team', link: 'team' },
      {
        text: '2.11.*',
        items: [
          { text: 'v3', link: '/v3/' },
          { text: 'Changelog', link: 'https://github.com/nexios-labs/nexios/blob/v3/CHANGELOG.md' },
          { text: 'Contributing', link: '/community/contribution-guide' },
        ]
      }
    ],

    sidebar: {
      '/intro/': [
        { text: 'What is Nexios?', link: '/intro' },
        { text: "What is Asgi?", link: '/intro/asgi' },
        { text: 'Nexios And FastAPI', link: '/intro/nexios-and-fastapi' },
        { text: "Quick Start", link: '/intro/quick-start' },
        { text : "Core Concepts", link: '/intro/concepts' },
        { text : "Async Python", link: '/intro/async-python' },
        {text: 'Migrating To Nexios',link: '/intro/migrating-to-nexios'},
      ],
      '/community/': [
        { text: 'Welcome', link: '/community' },
        { text: 'FAQ', link: '/community/faq' },
        { text : "Contribution Guide", link:"/community/contribution-guide"},
        { text: 'Discussions', link: 'https://github.com/orgs/nexios-labs/discussions' },
        { text: 'Team', link: '/team' },
      ],
      '/guide/': [
        
        { text: 'Getting Started', link: '/guide/getting-started' },
        { text: 'CLI', link: '/guide/cli' },
        { text : "Why Nexios?", link: '/guide/why-nexios' },
        {
          text: 'Core Concepts',
          collapsed: false,
          items: [
            { text: 'Routing', link: '/guide/routing' },
            { text: 'Handlers', link: '/guide/handlers' },
            { text: 'Startups and Shutdowns', link: '/guide/startups-and-shutdowns' },
            { text: 'Request Inputs', link: '/guide/request-inputs' },
            { text: 'Configuration', link: '/guide/configuration' },
            { text: 'Sending Responses', link: '/guide/sending-responses' },
            { text: 'Routers and Subapps', link: '/guide/routers-and-subapps' },
            { text: 'Middleware', link: '/guide/middleware' },
          ] 
        },
        {
          text: 'Request Lifecycle',
          collapsed: false,
          items: [
            { text: 'Cookies', link: '/guide/cookies' },
            { text: 'Headers', link: '/guide/headers' },
            { text: 'Sessions', link: '/guide/sessions' },
            { text: 'Request Info', link: '/guide/request-info' },
          ]
        },
        {
          text: 'Advanced Topics',
          collapsed: false,
          items: [
            { text: 'Error Handling', link: '/guide/error-handling' },
            { text: 'Pagination', link: '/guide/pagination' },
            { text: 'Authentication', link: '/guide/authentication' },
            { text: "Handler Hooks", link: '/guide/handler-hooks' },
            { text: 'Class Based Handlers', link: '/guide/class-based-handlers' },
            { text: 'Events', link: '/guide/events' },
            { text: 'Streaming Response',  link: '/guide/streaming-response' },
            { text: 'Dependency Injection', link: '/guide/dependency-injection' },
            { text : "Templating", link:"/guide/templating/index"},
            { text: 'Static Files', link: '/guide/static-files' },
            { text: 'File Upload', link: '/guide/file-upload' },
            { text: 'Cors', link: '/guide/cors' },
            { text: 'CSRF', link: '/guide/csrf' },
            { text: 'File Router', link: '/guide/file-router' },
            { text: 'Concurrency Utilities', link: '/guide/concurrency' },
            { text: 'Security', link: '/guide/security' },
            { text: 'Pydantic Integration', link: '/guide/pydantic-integration' },
          ]
        },
        {
          text: 'Websockets',
          collapsed: false,
          items: [
            { text: 'Overview', link: '/guide/websockets/index' },
            { text: 'Channels', link: '/guide/websockets/channels' },
            { text: 'Groups', link: '/guide/websockets/groups' },
            { text: 'Events', link: '/guide/websockets/events' },
            { text: 'Consumer', link: '/guide/websockets/consumer' },
          ]
        },
        {
          text: 'OpenAPI',
          collapsed: false,
          items: [
            { text: 'Overview', link: '/guide/openapi/index' },
            { text: 'Response Models with Pydantic', link: '/guide/openapi/response-models' },
            { text: 'Request Schemas', link: '/guide/openapi/request-schemas' },
            { text: 'Request Parameters', link: '/guide/openapi/request-parameters' },
            { text: 'Customizing OpenAPI Config', link: '/guide/openapi/customizing-openapi-configuration' },
            { text: 'Authentication Docs', link: '/guide/openapi/authentication-documentation' },
          ]
        }
      ],
      '/v3/guide/': [
        
        { text: 'Getting Started', link: '/v3/guide/getting-started' },
        { text: 'CLI', link: '/v3/guide/cli' },
        { text : "Why Nexios?", link: '/v3/guide/why-nexios' },
        {
          text: 'Core Concepts',
          collapsed: false,
          items: [
            { text: 'Routing', link: '/v3/guide/routing' },
            { text: 'Handlers', link: '/v3/guide/handlers' },
            { text: 'Startups and Shutdowns', link: '/v3/guide/startups-and-shutdowns' },
            { text: 'Request Inputs', link: '/v3/guide/request-inputs' },
            { text: 'Configuration', link: '/v3/guide/configuration' },
            { text: 'Sending Responses', link: '/v3/guide/sending-responses' },
            { text: 'Routers and Subapps', link: '/v3/guide/routers-and-subapps' },
            { text: 'Middleware', link: '/v3/guide/middleware' },
          ] 
        },
        {
          text: 'Request Lifecycle',
          collapsed: false,
          items: [
            { text: 'Cookies', link: '/v3/guide/cookies' },
            { text: 'Headers', link: '/v3/guide/headers' },
            { text: 'Sessions', link: '/v3/guide/sessions' },
            { text: 'Request Info', link: '/v3/guide/request-info' },
          ]
        },
        {
          text: 'Advanced Topics',
          collapsed: false,
          items: [
            { text: 'Error Handling', link: '/v3/guide/error-handling' },
            { text: 'Pagination', link: '/v3/guide/pagination' },
            { text: 'Authentication', link: '/v3/guide/authentication' },
            { text: "Handler Hooks", link: '/v3/guide/handler-hooks' },
            { text: 'Class Based Handlers', link: '/v3/guide/class-based-handlers' },
            { text: 'Events', link: '/v3/guide/events' },
            { text: 'Streaming Response',  link: '/v3/guide/streaming-response' },
            { text: 'Dependency Injection', link: '/v3/guide/dependency-injection' },
            { text : "Templating", link:"/v3/guide/templating/index"},
            { text: 'Static Files', link: '/v3/guide/static-files' },
            { text: 'File Upload', link: '/v3/guide/file-upload' },
            { text: 'Cors', link: '/v3/guide/cors' },
            { text: 'CSRF', link: '/v3/guide/csrf' },
            { text: 'File Router', link: '/v3/guide/file-router' },
            { text: 'Concurrency Utilities', link: '/v3/guide/concurrency' },
            { text: 'Security', link: '/v3/guide/security' },
            { text: 'Pydantic Integration', link: '/v3/guide/pydantic-integration' },
          ]
        },
        {
          text: 'Websockets',
          collapsed: false,
          items: [
            { text: 'Overview', link: '/v3/guide/websockets/index' },
            { text: 'Channels', link: '/v3/guide/websockets/channels' },
            { text: 'Groups', link: '/v3/guide/websockets/groups' },
            { text: 'Events', link: '/v3/guide/websockets/events' },
            { text: 'Consumer', link: '/v3/guide/websockets/consumer' },
          ]
        },
        {
          text: 'OpenAPI',
          collapsed: false,
          items: [
            { text: 'Overview', link: '/v3/guide/openapi/index' },
            { text: 'Response Models with Pydantic', link: '/v3/guide/openapi/response-models' },
            { text: 'Request Schemas', link: '/v3/guide/openapi/request-schemas' },
            { text: 'Request Parameters', link: '/v3/guide/openapi/request-parameters' },
            { text: 'Customizing OpenAPI Config', link: '/v3/guide/openapi/customizing-openapi-configuration' },
            { text: 'Authentication Docs', link: '/v3/guide/openapi/authentication-documentation' },
          ]
        }
      ]
     
    }
  },

  markdown: {
    // lineNumbers: true
  },

  ignoreDeadLinks: true,
})
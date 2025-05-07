// docs/.vitepress/config.js

export default {
    title: 'Nexios',
    description: 'Async web framework for Python',
    themeConfig: {
      logo: '/icon.svg',
      nav: [
        { text: 'Guide', link: '/guide/getting-started' },
        { text: 'API Reference', link: '/guide/api-reference' },
        { text: 'GitHub', link: 'https://github.com/nexios-labs/Nexios' }
      ],
      sidebar: [
        {
          "text": "Architecture",
          "items": [
            { text: 'Async Python', link: '/architecture/async-python' },
            { text: 'Asgi', link: '/architecture/asgi' },
           
          ],

          
        },

        {
          "text": "Guide",
          "items": [
            { text: 'Getting Started', link: '/guide/getting-started' },
            { text: 'Routing', link: '/guide/routing' },
            { text : "Handlers", link: "/guide/handlers" },
            { text : "Startups and Shutdowns", link: "/guide/startups-and-shutdowns" },
            { text : "Request Inputs", link: "/guide/request-inputs" },
            { text : "Configuration", link: "/guide/configuration" },
            { text: 'API Reference', link: '/guide/api-reference' },
          ]
        },
      ]
    },
    markdown: {
        lineNumbers: true
      }
  }
  
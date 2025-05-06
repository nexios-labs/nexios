// docs/.vitepress/config.js

export default {
    title: 'Nexios',
    description: 'Async web framework for Python',
    themeConfig: {
      logo: '/icon.svg',
      nav: [
        { text: 'Guide', link: '/guide/getting-started' },
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
            { text: 'API Reference', link: '/guide/api-reference' },
          ]
        },
      ]
    },
    markdown: {
        lineNumbers: true
      }
  }
  
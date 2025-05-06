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
            { text: 'Request and Response', link: '/guide/request-and-response' },
            { text: 'Error Handling', link: '/guide/error-handling' },
            { text: 'Static Files', link: '/guide/static-files' },
            { text: 'Middleware', link: '/guide/middleware' },
            { text: 'Processing Inputs', link: '/guide/processing-inputs' }
          ]
        }
      ]
    },
    markdown: {
        lineNumbers: true
      }
  }
  
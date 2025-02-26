module.exports = {
    entry: "index.html", // Main Docsify entry file
    output: "dist", // Where the pre-rendered files go
    routes: ["/", "/introduction", "/guide", "/comparison"], // Define the pages to pre-render
    port: 3000, // Server port
  };
  
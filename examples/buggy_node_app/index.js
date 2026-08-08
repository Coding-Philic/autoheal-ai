// A deliberately buggy Node.js app for testing AutoHeal
const http = require('http');

const server = http.createServer((req, res) => {
    // BUG: Accessing property of undefined
    const config = undefined;
    const port = config.port;  // TypeError: Cannot read properties of undefined

    res.writeHead(200);
    res.end('Hello World');
});

server.listen(3456, () => {
    console.log('Server running on port 3456');
});

// Trigger the error
setTimeout(() => {
    http.get('http://localhost:3456', (res) => {
        console.log('Response received');
    });
}, 500);

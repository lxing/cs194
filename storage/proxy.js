var http = require('http'),
    httpProxy = require('http-proxy');
//
// Create your proxy server and set the target in the options.
//
httpProxy.createProxyServer({
  target:'http://www.ncbi.nlm.nih.gov/'
}).listen(8000);
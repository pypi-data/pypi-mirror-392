console.log(opts);
const getParameterProxyHandler = {
  apply: function (target, ctx, args) {
    const param = (args || [])[0];

    if (param === 37445) {
      return opts.webgl_vendor || "Intel Inc.";
    }

    if (param === 37446) {
      return opts.webgl_renderer || "Intel Iris OpenGL Engine";
    }
    return utils.cache.Reflect.apply(target, ctx, args);
  },
};

const addProxy = (obj, propName) => {
  utils.replaceWithProxy(obj, propName, getParameterProxyHandler);
};

addProxy(WebGLRenderingContext.prototype, "getParameter");
addProxy(WebGL2RenderingContext.prototype, "getParameter");

generateFunctionMocks = (proto, itemMainProp, dataArray) => ({
  item: utils.createProxy(proto.item, {
    apply(target, ctx, args) {
      if (!args.length) {
        throw new TypeError(
          `Failed to execute 'item' on '${
            proto[Symbol.toStringTag]
          }': 1 argument required, but only 0 present.`,
        );
      }

      const isInteger = args[0] && Number.isInteger(Number(args[0]));

      return (isInteger ? dataArray[Number(args[0])] : dataArray[0]) || null;
    },
  }),

  namedItem: utils.createProxy(proto.namedItem, {
    apply(target, ctx, args) {
      if (!args.length) {
        throw new TypeError(
          `Failed to execute 'namedItem' on '${
            proto[Symbol.toStringTag]
          }': 1 argument required, but only 0 present.`,
        );
      }
      return dataArray.find((mt) => mt[itemMainProp] === args[0]) || null;
    },
  }),

  refresh: proto.refresh
    ? utils.createProxy(proto.refresh, {
        apply(target, ctx, args) {
          return undefined;
        },
      })
    : undefined,
});

function generateMagicArray(
  dataArray = [],
  proto = MimeTypeArray.prototype,
  itemProto = MimeType.prototype,
  itemMainProp = "type",
) {
  const defineProp = (obj, prop, value) =>
    Object.defineProperty(obj, prop, {
      value,
      writable: false,
      enumerable: false,
      configurable: false,
    });

  const makeItem = (data) => {
    const item = {};
    for (const prop of Object.keys(data)) {
      if (prop.startsWith("__")) {
        continue;
      }
      defineProp(item, prop, data[prop]);
    }

    if (itemProto === Plugin.prototype) {
      defineProp(item, "length", 1);
    }

    return Object.create(itemProto, Object.getOwnPropertyDescriptors(item));
  };

  const magicArray = [];

  dataArray.forEach((data) => {
    magicArray.push(makeItem(data));
  });

  magicArray.forEach((entry) => {
    defineProp(magicArray, entry[itemMainProp], entry);
  });

  const magicArrayObj = Object.create(proto, {
    ...Object.getOwnPropertyDescriptors(magicArray),

    length: {
      value: magicArray.length,
      writable: false,
      enumerable: false,
      configurable: true,
    },
  });

  const functionMocks = generateFunctionMocks(proto, itemMainProp, magicArray);

  return new Proxy(magicArrayObj, {
    get(target, key = "") {
      if (key === "item") {
        return functionMocks.item;
      }
      if (key === "namedItem") {
        return functionMocks.namedItem;
      }
      if (proto === PluginArray.prototype && key === "refresh") {
        return functionMocks.refresh;
      }

      return utils.cache.Reflect.get(...arguments);
    },
    ownKeys(target) {
      const keys = [];
      const typeProps = magicArray.map((mt) => mt[itemMainProp]);
      typeProps.forEach((_, i) => keys.push(`${i}`));
      typeProps.forEach((propName) => keys.push(propName));
      return keys;
    },
  });
}

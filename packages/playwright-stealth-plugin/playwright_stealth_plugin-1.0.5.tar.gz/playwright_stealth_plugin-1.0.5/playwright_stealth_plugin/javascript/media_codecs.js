const parseInput = (arg) => {
  const [mime, codecStr] = arg.trim().split(";");
  let codecs = [];
  if (codecStr && codecStr.includes('codecs="')) {
    codecs = codecStr
      .trim()
      .replace(`codecs="`, "")
      .replace(`"`, "")
      .trim()
      .split(",")
      .filter((x) => !!x)
      .map((x) => x.trim());
  }
  return {
    mime,
    codecStr,
    codecs,
  };
};

const canPlayType = {
  apply: function (target, ctx, args) {
    if (!args || !args.length) {
      return target.apply(ctx, args);
    }
    const { mime, codecs } = parseInput(args[0]);

    if (mime === "video/mp4") {
      if (codecs.includes("avc1.42E01E")) {
        return "probably";
      }
    }

    if (mime === "audio/x-m4a" && !codecs.length) {
      return "maybe";
    }

    if (mime === "audio/aac" && !codecs.length) {
      return "probably";
    }

    return target.apply(ctx, args);
  },
};

utils.replaceWithProxy(HTMLMediaElement.prototype, "canPlayType", canPlayType);

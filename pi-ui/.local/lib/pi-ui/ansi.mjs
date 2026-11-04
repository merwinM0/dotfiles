// Remove only painted backgrounds, preserving foreground colors, OSC links and text.
export function transparentSgr(text) {
  return text.replace(/\x1b\[([\d:;]*)m/g, (sequence, parameters) => {
    const input = parameters.split(";");
    const output = [];
    for (let index = 0; index < input.length; index++) {
      const item = input[index];
      const code = Number(item.split(":", 1)[0]);
      if (code === 38 || code === 48 || code === 58) {
        const length = item.includes(":") ? 1 : input[index + 1] === "2" ? 5 : input[index + 1] === "5" ? 3 : 1;
        if (code === 48) output.push("49");
        else output.push(...input.slice(index, index + length));
        index += length - 1;
      } else if ((code >= 40 && code <= 47) || (code >= 100 && code <= 107)) {
        output.push("49");
      } else if (code === 7) {
        // Reverse video paints a background too; retain emphasis without filling cells.
        output.push("1", "4");
      } else {
        output.push(item);
      }
    }
    return `\x1b[${output.join(";")}m`;
  });
}

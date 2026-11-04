import { transparentSgr } from "./ansi.mjs";

// Dependencies come from the SAME installed pi-tui instance as the unbundled CLI.
export function createFrameSystem({ tui, dispatchMouseEvent, isImageLine, theme }) {
  const { visibleWidth, truncateToWidth, stripTerminalSequences } = tui;
  const decorated = new WeakMap();

  class CornerFrame {
    constructor(child, { role = "accent", label = "", gap = false } = {}) {
      this.child = child;
      this.role = role;
      this.label = label;
      this.gap = gap;
    }

    invalidate() {
      this.layout = undefined;
      this.child.invalidate?.();
    }

    render(width) {
      if (width <= 0) {
        this.layout = undefined;
        return [];
      }
      if (width < 8) {
        this.layout = { framed: false };
        return this.child.render(width).map(line => {
          if (isImageLine(line)) return line;
          const transparent = transparentSgr(line);
          return visibleWidth(transparent) > width ? truncateToWidth(transparent, width, "") : transparent;
        });
      }
      const innerWidth = width - 2;
      const raw = this.child.render(innerWidth);
      const blank = line => !isImageLine(line) && !line.includes("\x1b]133;") && !stripTerminalSequences(line).trim();
      let first = 0;
      let last = raw.length;
      while (first < last && blank(raw[first])) first++;
      while (last > first && blank(raw[last - 1])) last--;
      if (first === last) {
        this.layout = undefined;
        return [];
      }
      const body = raw.slice(first, last);
      const role = typeof this.role === "function" ? this.role(raw) : this.role;
      const label = typeof this.label === "function" ? this.label() : this.label;
      const title = truncateToWidth(stripTerminalSequences(String(label)), width - 8, "");
      const left = title ? `┏━ ${title} ` : "┏━";
      const color = text => theme.fg(role, text);
      const top = color(left + "━".repeat(Math.max(0, width - visibleWidth(left) - 1)) + "┓");
      const bottom = color("┗" + "━".repeat(width - 2) + "┛");
      const lines = body.map(line => {
        // Graphics lines contain protocol metadata and must not be sliced or prefixed.
        if (isImageLine(line)) return line;
        const transparent = transparentSgr(line);
        const fitted = visibleWidth(transparent) > innerWidth ? truncateToWidth(transparent, innerWidth, "") : transparent;
        return `\x1b[49m${color("┃")}${fitted}\x1b[49m${" ".repeat(Math.max(0, innerWidth - visibleWidth(fitted)))}${color("┃")}`;
      });
      const gap = this.gap ? 1 : 0;
      this.layout = { framed: true, innerWidth, first, rawHeight: raw.length, bodyHeight: body.length, gap };
      return [...(gap ? [""] : []), `\x1b[49m${top}`, ...lines, `\x1b[49m${bottom}`];
    }

    handleInput(data) {
      this.child.handleInput?.(data);
    }

    handleMouse(event) {
      const layout = this.layout;
      if (!layout) return undefined;
      if (!layout.framed) return dispatchMouseEvent(this.child, event);
      const y = event.y - layout.gap - 1;
      const x = event.x - 1;
      if (x < 0 || x >= layout.innerWidth || y < 0 || y >= layout.bodyHeight) return undefined;
      return dispatchMouseEvent(this.child, {
        ...event, x, y: y + layout.first, width: layout.innerWidth, height: layout.rawHeight,
      });
    }
  }

  // Preserve component identity: Pi stores references for status deduplication/removal.
  function decorate(component, options) {
    if (decorated.has(component)) return component;
    const child = {
      render: component.render.bind(component),
      invalidate: component.invalidate?.bind(component),
      handleMouse: component.handleMouse?.bind(component),
      handleInput: component.handleInput?.bind(component),
    };
    const frame = new CornerFrame(child, options);
    component.render = frame.render.bind(frame);
    component.handleMouse = frame.handleMouse.bind(frame);
    component.invalidate = frame.invalidate.bind(frame);
    decorated.set(component, frame);
    return component;
  }

  function decoratePrototype(prototype, options) {
    const render = prototype.render;
    const mouse = prototype.handleMouse;
    const frames = new WeakMap();
    prototype.render = function (width) {
      let frame = frames.get(this);
      if (!frame) {
        const owner = this;
        frame = new CornerFrame({
          render: columns => render.call(owner, columns),
          handleMouse: event => mouse?.call(owner, event),
          invalidate() {},
        }, typeof options === "function" ? options(owner) : options);
        frames.set(this, frame);
      }
      return frame.render(width);
    };
    prototype.handleMouse = function (event) {
      return frames.get(this)?.handleMouse(event);
    };
  }

  return { CornerFrame, decorate, decoratePrototype };
}

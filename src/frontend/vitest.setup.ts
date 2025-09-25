import "@testing-library/jest-dom/vitest";

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

const originalConsoleError = console.error;
const originalConsoleWarn = console.warn;

beforeEach(() => {
  vi.restoreAllMocks();
  vi.spyOn(console, "error").mockImplementation((message?: unknown, ...args: unknown[]) => {
    if (typeof message === "string") {
      if (message.includes("not wrapped in act")) {
        return;
      }
      if (message.includes("ReactDOMTestUtils.act is deprecated")) {
        return;
      }
      if (message.includes("current testing environment is not configured to support act")) {
        return;
      }
    }
    originalConsoleError.call(console, message, ...args);
  });
  vi.spyOn(console, "warn").mockImplementation((message?: unknown, ...args: unknown[]) => {
    if (typeof message === "string" && message.includes("React Router Future Flag Warning")) {
      return;
    }
    originalConsoleWarn.call(console, message, ...args);
  });
});

if (typeof window !== "undefined" && !window.matchMedia) {
  window.matchMedia = () => ({
    matches: false,
    media: "",
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  });
}

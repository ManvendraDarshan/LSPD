import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import App from "./App";
import { AuthProvider } from "./context/AuthContext";

describe("App", () => {
  it("renders the LSPD brand", () => {
    window.history.pushState({}, "", "/about");
    render(<AuthProvider><App /></AuthProvider>);
    expect(screen.getAllByText("LSPD").length).toBeGreaterThan(0);
  });
});

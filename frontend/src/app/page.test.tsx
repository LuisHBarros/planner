import { render, screen } from "@testing-library/react";
import React from "react";
import Page from "./page";

vi.mock("../components/AppShell", () => ({
  AppShell: () => <div>Planner MVP</div>
}));

describe("Planner frontend MVP", () => {
  it("renders the shell", () => {
    render(<Page />);
    expect(screen.getByText("Planner MVP")).toBeInTheDocument();
  });
}
);


import { defineConfig } from "orval";

export default defineConfig({
  caragent: {
    input: {
      target: "./openapi/openapi.json",
    },
    output: {
      target: "./src/generated/client.ts",
      client: "react-query",
      clean: true,
    },
  },
});

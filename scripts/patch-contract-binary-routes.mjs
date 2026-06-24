import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(scriptDir, "..");
const clientPath = resolve(repoRoot, "packages/contracts/src/generated/client.ts");

const operationName = "getArtifactContentWorkspacesWorkspaceIdArtifactsArtifactIdContentGet";
const responseType = `${operationName}Response`;
const functionPattern = new RegExp(
  `export const ${operationName} = async \\(workspaceId: string,\\s*\\n\\s*artifactId: string, options\\?: RequestInit\\): Promise<${responseType}> => \\{[\\s\\S]*?\\n\\}\\n`,
);

const content = readFileSync(clientPath, "utf8");
const match = content.match(functionPattern);

if (!match) {
  throw new Error(`Could not find generated operation ${operationName} in ${clientPath}.`);
}

const replacement = `export const ${operationName} = async (workspaceId: string,
    artifactId: string, options?: RequestInit): Promise<${responseType}> => {

  const res = await fetch(getGetArtifactContentWorkspacesWorkspaceIdArtifactsArtifactIdContentGetUrl(workspaceId,artifactId),
  {
    ...options,
    method: 'GET'


  }
)

  const data: ${responseType}['data'] = [204, 205, 304].includes(res.status)
    ? {}
    : res.ok
      ? await res.blob()
      : await res.json()
  return { data, status: res.status, headers: res.headers } as ${responseType}
}
`;

writeFileSync(clientPath, content.replace(functionPattern, replacement));

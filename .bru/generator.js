const fs = require("fs");
const path = require("path");

const spec = JSON.parse(fs.readFileSync("openapi.json", "utf-8"));

const BASE_DIR = "book-library-api";

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function writeFile(filePath, content) {
  fs.writeFileSync(filePath, content);
}

function toBru({ name, method, url, query = null, body = null }) {
  let q = "";
  if (query) {
    q =
      "query {\n" +
      Object.entries(query)
        .map(([k, v]) => `  ${k}: ${v ?? ""}`)
        .join("\n") +
      "\n}";
  }

  let b = "";
  if (body) {
    b = `body:json {\n${JSON.stringify(body, null, 2)}\n}`;
  }

  return `meta {
  name: ${name}
  type: http
}

${method.toLowerCase()} {
  url: {{baseUrl}}${url}
}

${q}

${b}
`;
}

// Create base structure
ensureDir(BASE_DIR);

// bruno.json
writeFile(
  path.join(BASE_DIR, "bruno.json"),
  JSON.stringify(
    {
      version: "1",
      name: spec.info.title,
      type: "collection",
      format: "bruno",
      ignore: [],
      env: {
        baseUrl: "http://localhost:8000"
      }
    },
    null,
    2
  )
);
// Helpers to map OpenAPI paths
function getTagFolder(tags) {
  return tags?.[0] || "General";
}

function createRequestFile(folder, fileName, content) {
  const dir = path.join(BASE_DIR, folder);
  ensureDir(dir);
  writeFile(path.join(dir, fileName), content);
}

// Iterate paths
for (const [route, methods] of Object.entries(spec.paths)) {
  for (const [method, details] of Object.entries(methods)) {
    const tag = getTagFolder(details.tags);
    const folder = tag.replace(/\s+/g, "");

    const name = details.summary || `${method.toUpperCase()} ${route}`;

    let url = route;

    // Convert OpenAPI params {id} → {{id}}
    url = url.replace(/\{(.*?)\}/g, "{{$1}}");

    let query = null;
    let body = null;

    // Query params
    if (details.parameters) {
      const q = details.parameters.filter((p) => p.in === "query");
      if (q.length) {
        query = {};
        q.forEach((p) => (query[p.name] = ""));
      }
    }

    // Body
    if (details.requestBody) {
      const schema =
        details.requestBody.content?.["application/json"]?.schema;

      body = schema?.$ref
        ? { example: schema.$ref }
        : {};
    }

    const bru = toBru({
      name,
      method,
      url,
      query,
      body,
    });

    const fileName =
      route
        .replace(/\//g, "_")
        .replace(/\{|\}/g, "")
        .replace(/_+/g, "_")
        .replace(/^_+/, "") +
      `_${method}.bru`;

    createRequestFile(folder, fileName, bru);
  }
}

console.log("✅ Bruno collection generated in:", BASE_DIR);


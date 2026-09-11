import { createServer } from "node:http";
import { Readable } from "node:stream";

import handler from "./client/dist/server/server.js";

const port = Number(process.env.PORT ?? 3000);
const host = process.env.HOST ?? "0.0.0.0";

function requestHeaders(headers) {
  return Object.fromEntries(
    Object.entries(headers)
      .filter(([, value]) => value !== undefined)
      .map(([name, value]) => [name, Array.isArray(value) ? value.join(", ") : value]),
  );
}

const server = createServer(async (incoming, outgoing) => {
  try {
    const protocol = incoming.headers["x-forwarded-proto"] ?? "http";
    const url = new URL(
      incoming.url ?? "/",
      `${protocol}://${incoming.headers.host ?? `${host}:${port}`}`,
    );
    const method = incoming.method ?? "GET";
    const request = new Request(url, {
      method,
      headers: requestHeaders(incoming.headers),
      body: method === "GET" || method === "HEAD" ? undefined : incoming,
      duplex: "half",
    });
    const response = await handler.fetch(request, process.env, {});

    outgoing.statusCode = response.status;
    response.headers.forEach((value, name) => outgoing.setHeader(name, value));
    if (method === "HEAD" || !response.body) {
      outgoing.end();
      return;
    }
    Readable.fromWeb(response.body).pipe(outgoing);
  } catch (error) {
    console.error(error);
    outgoing.statusCode = 500;
    outgoing.end("Internal Server Error");
  }
});

server.listen(port, host, () => {
  console.log(`PALA frontend listening on ${host}:${port}`);
});
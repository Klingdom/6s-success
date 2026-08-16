/* ai-proxy-example.js — minimal AI proxy for the 6S Home Micro Zones beta.
 *
 * WHY THIS EXISTS
 * The app must never hold the API key. This tiny server holds the key, forwards
 * the app's Anthropic-style /v1/messages body to Anthropic, and returns the reply.
 * Point the app at this server's URL in Settings -> AI endpoint.
 *
 * This is a starting example, not production. Before real testers use it, add:
 *   - per-user or per-device metering and a hard analysis cap
 *   - a zero-retention / no-training API configuration, and document it
 *   - request-size limits and basic abuse protection
 *   - the current model id (confirm at build time) and a sensible max_tokens
 *
 * RUN
 *   npm init -y && npm install express
 *   ANTHROPIC_API_KEY=sk-... node ai-proxy-example.js
 * then in the app Settings set the endpoint to  http://<your-host>:8787/ai
 */
const express = require("express");
const app = express();
app.use(express.json({ limit: "8mb" }));

// CORS so the app (served from another origin) can call this.
app.use((req, res, next) => {
  res.set("Access-Control-Allow-Origin", "*");
  res.set("Access-Control-Allow-Headers", "Content-Type");
  res.set("Access-Control-Allow-Methods", "POST, OPTIONS");
  if (req.method === "OPTIONS") return res.sendStatus(204);
  next();
});

app.post("/ai", async (req, res) => {
  try {
    const key = process.env.ANTHROPIC_API_KEY;
    if (!key) return res.status(500).json({ error: { message: "server missing ANTHROPIC_API_KEY" } });

    // The app sends { model, max_tokens, messages }. Pin the model here rather
    // than trusting the client, and confirm the current model id at build time.
    const body = {
      model: process.env.MODEL || "claude-sonnet-4-6",
      max_tokens: Math.min(req.body.max_tokens || 1200, 2000),
      messages: req.body.messages,
    };

    const r = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify(body),
    });
    const data = await r.json();
    res.status(r.status).json(data); // app expects the messages response shape
  } catch (e) {
    res.status(502).json({ error: { message: String(e && e.message || e) } });
  }
});

const PORT = process.env.PORT || 8787;
app.listen(PORT, () => console.log("6S AI proxy on :" + PORT + "  POST /ai"));

import Pusher from "pusher-js";
import fetch from "node-fetch";

const API_KEY = process.env.PNW_API_KEY;
const PUSHER_KEY = process.env.PNW_PUSHER_KEY;
const MODEL = process.env.PNW_MODEL; 
const EVENT_PREFIX = process.env.PNW_EVENT_PREFIX;

if (!API_KEY) {
  console.error("[NODE] ❌ PNW_API_KEY environment variable not set");
  process.exit(1);
}

if (!MODEL) {
  console.error("[NODE] ❌ PNW_MODEL environment variable not set");
  process.exit(1);
}

if (!EVENT_PREFIX) {
  console.error("[NODE] ❌ PNW_EVENT_PREFIX environment variable not set");
  process.exit(1);
}

const pusher = new Pusher(PUSHER_KEY, {
  cluster: "mt1",
  wsHost: "socket.politicsandwar.com",
  disableStats: true,
  authEndpoint: "https://api.politicsandwar.com/subscriptions/v1/auth",
});

pusher.connection.bind("connected", () => console.error("[NODE] ✅ Pusher connected"));
pusher.connection.bind("error", (err) => console.error("[NODE] ❌ Pusher error:", err));
pusher.connection.bind("disconnected", () => console.error("[NODE] ⚠️ Pusher disconnected"));

async function getChannel(model, event, metadata = false) {
  const url = new URL(`https://api.politicsandwar.com/subscriptions/v1/subscribe/${model}/${event}`);
  url.searchParams.append("api_key", API_KEY);
  url.searchParams.append("metadata", metadata ? "true" : "false");
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
  const data = await res.json();
  console.error(`[NODE] 📡 Got channel for ${model}/${event}: ${data.channel}`);
  return data.channel;
}

function extractData(eventType, data) {
  if (!data) return [];
  
  if (eventType.includes("BULK")) {
    if (Array.isArray(data)) return data;
    if (data.after && Array.isArray(data.after)) return data.after;
    if (data.metadata && Array.isArray(data.metadata)) return data.metadata;
    if (typeof data === "object") {
      const vals = Object.values(data);
      if (vals.length > 0 && typeof vals[0] === "object") return vals;
    }
  } else {
    if (Array.isArray(data)) return data;
    if (data.after && typeof data.after === "object") return [data.after];
    if (data.metadata && typeof data.metadata === "object") return [data.metadata];
    if (data.id) return [data];
  }
  
  return [];
}

function subscribeToEvents(channelName, eventType) {
  const channel = pusher.subscribe(channelName);

  channel.bind_global((eventName, data) => {
    try {
      const items = extractData(eventName, data);

      for (const item of items) {
        if (!item.id && !item.nation_id && !item.war_id && !item.city_id && !item.alliance_id && !item.trade_id) {
          continue;
        }

        const event = {
          type: eventType,
          ...item
        };

        console.log(JSON.stringify(event));
      }
    } catch (err) {
      console.error("[NODE] ❌ Error handling event:", err);
    }
  });
}

(async () => {
  try {
    const createChannel = await getChannel(MODEL, "create", true);
    subscribeToEvents(createChannel, `${EVENT_PREFIX}_CREATED`);
    console.error(`[NODE] 🚀 ${MODEL} create listener active`);

    try {
      const updateChannel = await getChannel(MODEL, "update", true);
      subscribeToEvents(updateChannel, `${EVENT_PREFIX}_UPDATED`);
      console.error(`[NODE] 🚀 ${MODEL} update listener active`);
    } catch (err) {
      console.error(`[NODE] ℹ️ ${MODEL} update not available`);
    }

    try {
      const deleteChannel = await getChannel(MODEL, "delete", true);
      subscribeToEvents(deleteChannel, `${EVENT_PREFIX}_DELETED`);
      console.error(`[NODE] 🚀 ${MODEL} delete listener active`);
    } catch (err) {
      console.error(`[NODE] ℹ️ ${MODEL} delete not available`);
    }

    console.error(`[NODE] ✅ All ${MODEL} listeners active`);
  } catch (err) {
    console.error("[NODE] ❌ Failed to initialize:", err);
    process.exit(1);
  }
})();
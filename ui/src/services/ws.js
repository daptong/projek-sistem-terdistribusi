// Simple WebSocket client with auto-reconnect and message callback
const WS_URL = (() => {
  const loc = window.location
  return (loc.protocol === 'https:' ? 'wss://' : 'ws://') + loc.host + '/ws'
})();

export function connectWebSocket(onMessage, opts = {}) {
  // opts: { onOpen: fn, onClose: fn }
  let ws = null
  let closedByUser = false
  let reconnectTimer = null

  function create() {
    ws = new WebSocket(WS_URL)

    ws.onopen = () => {
      console.log('[ws] connected')
      if (reconnectTimer) {
        clearTimeout(reconnectTimer)
        reconnectTimer = null
      }
      try { opts.onOpen && opts.onOpen() } catch (e) { console.warn(e) }
    }

    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data)
        onMessage && onMessage(data)
      } catch (e) {
        console.warn('[ws] invalid message', e)
      }
    }

    ws.onclose = () => {
      console.log('[ws] closed')
      try { opts.onClose && opts.onClose() } catch (e) { console.warn(e) }
      if (!closedByUser) {
        // simple reconnect
        reconnectTimer = setTimeout(create, 2000)
      }
    }

    ws.onerror = (err) => {
      console.warn('[ws] error', err)
      try {
        ws.close()
      } catch (e) {}
    }
  }

  create()

  return {
    close: () => {
      closedByUser = true
      if (reconnectTimer) clearTimeout(reconnectTimer)
      try {
        ws && ws.close()
      } catch (e) {}
    },
  }
}

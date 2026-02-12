const API_BASE = '';
const WS_BASE = `${location.protocol === 'https:' ? 'wss:' : 'ws:'}//${location.host}`;

let ws = null;

let formCreateLot, createMessage, btnRefreshLots, lotsList, lotsMessage, wsStatus, wsEvents;

function showMessage(el, text, type = '') {
  if (!el) return;
  el.textContent = text;
  el.className = 'message' + (type ? ` ${type}` : '');
}

async function createLot(e) {
  e.preventDefault();
  const form = e.target;
  const title = form.title.value.trim();
  const start_price = parseFloat(form.start_price.value);
  if (!title || isNaN(start_price) || start_price < 0) {
    showMessage(createMessage, 'Invalid title or price', 'error');
    return;
  }
  showMessage(createMessage, 'Creating…');
  try {
    const res = await fetch(API_BASE + '/lots', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, start_price }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      showMessage(createMessage, data.detail || res.statusText || 'Error', 'error');
      return;
    }
    showMessage(createMessage, `Lot #${data.id} created.`, 'success');
    form.reset();
    loadLots();
  } catch (err) {
    showMessage(createMessage, 'Network error: ' + err.message, 'error');
  }
}

function escapeHtml(s) {
  const div = document.createElement('div');
  div.textContent = s;
  return div.innerHTML;
}

function formatPrice(value) {
  const n = typeof value === 'number' ? value : parseFloat(value);
  return isNaN(n) ? '0.00' : n.toFixed(2);
}

function updateLotCardPrice(lotId, currentPrice) {
  const card = document.querySelector(`.lot-card[data-lot-id="${lotId}"]`);
  if (!card) return;
  const priceEl = card.querySelector('.lot-current-price');
  if (priceEl) priceEl.textContent = formatPrice(currentPrice);
  const amountInput = card.querySelector('.bid-amount');
  if (amountInput) {
    const min = parseFloat(currentPrice);
    amountInput.min = min;
    amountInput.placeholder = (min + (min >= 1 ? 1 : 0.01)).toFixed(2);
  }
}

async function loadLots() {
  showMessage(lotsMessage, '');
  lotsList.innerHTML = '';
  try {
    const res = await fetch(API_BASE + '/lots');
    const data = await res.json().catch(() => []);
    if (!res.ok) {
      showMessage(lotsMessage, data.detail || res.statusText || 'Failed to load lots', 'error');
      return;
    }
    if (!Array.isArray(data) || data.length === 0) {
      showMessage(lotsMessage, 'No active lots.');
      return;
    }
    data.forEach((lot) => {
      const startPrice = typeof lot.start_price === 'number' ? lot.start_price : parseFloat(lot.start_price);
      const currentPrice = lot.current_price != null ? lot.current_price : startPrice;
      const card = document.createElement('div');
      card.className = 'lot-card';
      card.dataset.lotId = lot.id;
      card.innerHTML = `
        <div class="lot-info">
          <p class="lot-title">${escapeHtml(lot.title)}</p>
          <p class="lot-meta">#${lot.id} · Start: ${formatPrice(startPrice)} · Current: <strong class="lot-current-price">${formatPrice(currentPrice)}</strong> · ${lot.status}</p>
        </div>
        <button type="button" class="lot-open lot-open-btn" data-lot-id="${lot.id}">Open & bid</button>
        <div class="lot-bid-inline lot-bid-inline-hidden">
          <h3 class="lot-bid-title">Place bid</h3>
          <form class="form form-inline lot-bid-form" data-lot-id="${lot.id}">
            <label>
              Your name
              <input type="text" class="bid-bidder" required placeholder="John" />
            </label>
            <label>
              Amount
              <input type="number" class="bid-amount" step="0.01" min="${currentPrice}" required placeholder="${(currentPrice + (currentPrice >= 1 ? 1 : 0.01)).toFixed(2)}" />
            </label>
            <button type="submit">Place bid</button>
          </form>
          <p class="message lot-bid-message" aria-live="polite"></p>
        </div>
      `;
      const openBtn = card.querySelector('.lot-open-btn');
      const bidInline = card.querySelector('.lot-bid-inline');
      openBtn.addEventListener('click', (ev) => {
        ev.stopPropagation();
        bidInline.classList.remove('lot-bid-inline-hidden');
        openBtn.classList.add('lot-open-btn-hidden');
      });
      card.querySelector('.lot-bid-form').addEventListener('submit', (ev) => placeBid(ev, lot.id, card));
      lotsList.appendChild(card);
    });
  } catch (err) {
    showMessage(lotsMessage, 'Network error: ' + err.message, 'error');
  }
}

async function placeBid(e, lotId, card) {
  e.preventDefault();
  const form = card.querySelector('.lot-bid-form');
  const msgEl = card.querySelector('.lot-bid-message');
  const bidder = form.querySelector('.bid-bidder').value.trim();
  const amountInput = form.querySelector('.bid-amount');
  const amount = parseFloat(amountInput.value);
  if (!bidder || isNaN(amount)) {
    showMessage(msgEl, 'Name and amount required', 'error');
    return;
  }
  showMessage(msgEl, 'Placing bid…');
  try {
    const res = await fetch(API_BASE + `/lots/${lotId}/bids`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ bidder, amount }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      showMessage(msgEl, data.detail || res.statusText || 'Error', 'error');
      return;
    }
    showMessage(msgEl, 'Bid placed.', 'success');
    const newMin = amount;
    amountInput.min = newMin;
    amountInput.placeholder = (newMin + (newMin >= 1 ? 1 : 0.01)).toFixed(2);
    amountInput.value = '';
    updateLotCardPrice(lotId, amount);
  } catch (err) {
    showMessage(msgEl, 'Network error: ' + err.message, 'error');
  }
}

function connectGlobalWs() {
  if (ws) return;
  const url = `${WS_BASE}/ws/lots`;
  if (wsStatus) wsStatus.textContent = 'Connecting…';
  try {
    ws = new WebSocket(url);
    ws.onopen = () => {
      if (wsStatus) {
        wsStatus.textContent = 'Connected';
        wsStatus.className = 'ws-status connected';
      }
      addEventItem('Connected.', 'system');
    };
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        const lotPrefix = msg.lot_id != null ? `Lot #${msg.lot_id}: ` : '';
        if (msg.type === 'bid_placed') {
          addEventItem(`${lotPrefix}${msg.bidder} bid ${msg.amount}`, 'bid');
          if (msg.current_price != null && msg.lot_id != null) {
            updateLotCardPrice(msg.lot_id, msg.current_price);
          }
        } else if (msg.type === 'time_extended') {
          addEventItem(`${lotPrefix}Time extended until ${msg.new_end_time}`, 'time');
        } else if (msg.type === 'lot_ended') {
          addEventItem(`${lotPrefix}Auction ended.`, 'system');
          loadLots();
        } else {
          addEventItem(JSON.stringify(msg), 'system');
        }
      } catch {
        addEventItem(event.data, 'system');
      }
    };
    ws.onclose = () => {
      ws = null;
      if (wsStatus) {
        wsStatus.textContent = 'Disconnected';
        wsStatus.className = 'ws-status disconnected';
      }
    };
    ws.onerror = () => {
      if (wsStatus) {
        wsStatus.textContent = 'Error';
        wsStatus.className = 'ws-status error';
      }
    };
  } catch (err) {
    if (wsStatus) {
      wsStatus.textContent = 'Error: ' + err.message;
      wsStatus.className = 'ws-status error';
    }
  }
}

function addEventItem(text, type) {
  if (!wsEvents) return;
  const li = document.createElement('li');
  const span = document.createElement('span');
  span.className = 'event-type event-' + type;
  if (type === 'bid') span.textContent = 'Bid: ';
  else if (type === 'time') span.textContent = 'Time: ';
  else span.textContent = '';
  li.appendChild(span);
  li.appendChild(document.createTextNode(text));
  wsEvents.appendChild(li);
  wsEvents.scrollTop = wsEvents.scrollHeight;
}

function init() {
  formCreateLot = document.getElementById('form-create-lot');
  createMessage = document.getElementById('create-message');
  btnRefreshLots = document.getElementById('btn-refresh-lots');
  lotsList = document.getElementById('lots-list');
  lotsMessage = document.getElementById('lots-message');
  wsStatus = document.getElementById('ws-status');
  wsEvents = document.getElementById('ws-events');

  if (formCreateLot) formCreateLot.addEventListener('submit', createLot);
  if (btnRefreshLots) btnRefreshLots.addEventListener('click', loadLots);

  loadLots();
  connectGlobalWs();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

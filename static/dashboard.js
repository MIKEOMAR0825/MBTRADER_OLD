// -----------------------------
// Bascule état du bot
// -----------------------------
function toggleTrade() {
    fetch("/toggle_trade", { method: "POST" })
        .then(res => res.json())
        .then(data => {
            updateBotStatus(data.status === "ON");
        })
        .catch(err => console.error("Erreur toggleTrade:", err));
}

// -----------------------------
// Mise à jour status global du bot
// -----------------------------
function updateBotStatus(forceState = null) {
    fetch("/bot_status")
        .then(res => res.json())
        .then(data => {
            const running = forceState !== null ? forceState : data.running;
            document.getElementById("bot-status").innerText = running ? "🟢 ACTIF" : "🔴 ARRÊTÉ";

            // Solde
            document.getElementById("balance-available").innerText = data.balance.available.toFixed(2);
            document.getElementById("balance-locked").innerText = data.balance.locked.toFixed(2);

            // PnL global (réel + ouvert)
            const pnlElement = document.getElementById("total-pnl");
            pnlElement.innerText = data.pnl.total.toFixed(2);

            pnlElement.className = data.pnl.total >= 0 ? "green" : "red";

        })
        .catch(err => console.error("Erreur updateBotStatus:", err));
}

// -----------------------------
// Historique des trades
// -----------------------------
function updateTradeHistory() {
    fetch("/all_trades")
        .then(res => res.json())
        .then(data => {
            const table = document.getElementById("trade-history");
            table.innerHTML = "";

            data.forEach(trade => {
                const row = document.createElement("tr");

                row.innerHTML = `
                    <td>${trade.time_open ?? "-"}</td>
                    <td>${trade.action ?? "-"}</td>
                    <td>${trade.entry ?? "-"}</td>
                    <td>${trade.exit ?? (trade.status === "OPEN" ? "En cours" : "-")}</td>
                    <td class="${trade.pnl >= 0 ? "green" : "red"}">
                        ${trade.pnl !== undefined ? trade.pnl.toFixed(2) : "-"}
                    </td>
                    <td>${trade.status}</td>
                `;

                table.appendChild(row);
            });

        })
        .catch(err => console.error("Erreur updateTradeHistory:", err));
}

// -----------------------------
// Positions ouvertes
// -----------------------------
async function updatePositions() {
    try {
        const resp = await fetch("/dashboard_data");
        const data = await resp.json();

        const tbody = document.getElementById("positions-open");
        tbody.innerHTML = "";

        data.forEach(pos => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${pos.symbol}</td>
                <td>${pos.entry ?? "-"}</td>
                <td>${pos.quantity ?? "-"}</td>
                <td>${pos.stop_loss ?? "-"}</td>
                <td>${pos.take_profit ?? "-"}</td>
                <td>${pos.type}</td>
                <td class="${pos.pnl >= 0 ? "green" : "red"}">
                    ${pos.pnl !== undefined ? pos.pnl.toFixed(2) : "-"}
                </td>
            `;

            tbody.appendChild(row);
        });

    } catch (err) {
        console.error("Erreur updatePositions:", err);
    }
}

// -----------------------------
// STATS PRO (Winrate, PnL réel)
// -----------------------------
async function updateStats() {
    try {
        const res = await fetch("/pnl");
        const data = await res.json();

        // Total trades (fermés uniquement)
        document.getElementById("total-trades").innerText = data.total_trades;

        // PnL réel (fermés uniquement)
        const pnlElement = document.getElementById("total-pnl");
        pnlElement.innerText = data.total_pnl.toFixed(2);
        pnlElement.className = data.total_pnl >= 0 ? "green" : "red";

    } catch (err) {
        console.error("Erreur updateStats:", err);
    }
}

// -----------------------------
// Rafraîchissement automatique
// -----------------------------
function autoRefresh() {
    updateBotStatus();
    updateTradeHistory();
    updatePositions();
    updateStats(); // 🔥 important
}

// -----------------------------
// Initialisation
// -----------------------------
setInterval(autoRefresh, 3000);
autoRefresh();

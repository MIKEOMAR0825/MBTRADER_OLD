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

            // Solde disponible et bloqué
            document.getElementById("balance-available").innerText = data.balance.available.toFixed(2);
            document.getElementById("balance-locked").innerText = data.balance.locked.toFixed(2);

            // PnL
            document.getElementById("total-pnl").innerText = data.pnl.total.toFixed(2);

            const avg = total_trades > 0 ? total_pnl / total_trades : 0;
            document.getElementById("avg-pnl").innerText = avg.toFixed(2);
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
                const pnl = Number(trade.pnl ?? 0);

                row.innerHTML = `
                    <td>${trade.time_open ?? "-"}</td>
                    <td>${trade.action ?? "-"}</td>
                    <td>${trade.type ?? "-"}</td>
                    <td>${trade.entry ?? "-"}</td>
                    <td>${trade.exit ?? (trade.status === "OPEN" ? "En cours" : "-")}</td>
                    <td class="${pnl >= 0 ? "green" : "red"}">${pnl.toFixed(2)}</td>
                    <td>${trade.status}</td>
                `;
                table.appendChild(row);
            });

            // 🔥 IMPORTANT : uniquement CLOSED trades
            const closedTrades = data.filter(t => t.status === "CLOSED");

            const total_pnl = closedTrades.reduce((acc, t) => {
                return acc + Number(t.pnl ?? 0);
            }, 0);

            const avg_pnl = closedTrades.length > 0
                ? total_pnl / closedTrades.length
                : 0;

            document.getElementById("total-trades").innerText = closedTrades.length;
            document.getElementById("total-pnl").innerText = total_pnl.toFixed(2);
            document.getElementById("avg-pnl").innerText = avg_pnl.toFixed(2);
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
            const pnl = Number(pos.pnl ?? 0);

            row.innerHTML = `
                <td>${pos.symbol}</td>
                <td>${pos.entry ?? "-"}</td>
                <td>${pos.quantity ?? "-"}</td>
                <td>${pos.stop_loss ?? "-"}</td>
                <td>${pos.take_profit ?? "-"}</td>
                <td>${pos.type}</td>
                <td class="${pnl >= 0 ? "green" : "red"}">
                    ${pnl.toFixed(2)} USDT
                </td>            
                `;

            tbody.appendChild(row);
        });
    } catch (err) {
        console.error("Erreur updatePositions:", err);
    }
}

// -----------------------------
// Rafraîchissement automatique
// -----------------------------
function autoRefresh() {
    updateBotStatus();
    updateTradeHistory();
    updatePositions();
}

// -----------------------------
// Initialisation
// -----------------------------
setInterval(autoRefresh, 3000);
autoRefresh();
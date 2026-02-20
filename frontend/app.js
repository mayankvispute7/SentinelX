// frontend/app.js
const API_URL = "http://localhost:8000";
const API_KEY = "prod-super-secret-key-999"; // PHASE 3: Security Header
let localTransactionHistory = [];
let riskChartInstance = null;
let trendChartInstance = null;
let trendData = [0, 0, 0, 0, 0, 0]; 

function initCharts() {
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.font.family = 'sans-serif';

    const riskCtx = document.getElementById('riskChart').getContext('2d');
    riskChartInstance = new Chart(riskCtx, {
        type: 'doughnut',
        data: {
            labels: ['Low Risk', 'High/Medium Risk'],
            datasets: [{
                data: [1, 0], 
                backgroundColor: ['#10b981', '#ef4444'],
                borderWidth: 0,
                cutout: '75%'
            }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }
    });

    const trendCtx = document.getElementById('trendChart').getContext('2d');
    trendChartInstance = new Chart(trendCtx, {
        type: 'line',
        data: {
            labels: ['-50s', '-40s', '-30s', '-20s', '-10s', 'Now'],
            datasets: [{
                label: 'Fraud Rate %',
                data: trendData,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, max: 100 } } }
    });
}

async function fetchMetrics() {
    try {
        const response = await fetch(`${API_URL}/metrics`, {
            headers: { 'X-API-KEY': API_KEY } // Added Security Header
        });
        if (!response.ok) throw new Error("Network response was not ok");
        const data = await response.json();

        const total = data.total_transactions_processed || 0;
        const fraud = data.total_fraud_flags || 0;
        const rate = data.current_fraud_rate_percentage || 0;
        
        document.getElementById('kpiTotal').innerText = total;
        document.getElementById('kpiFraud').innerText = fraud;
        document.getElementById('kpiAvgRisk').innerText = (data.average_system_risk_score || 0).toFixed(4);

        const safe = total - fraud;
        riskChartInstance.data.datasets[0].data = [safe > 0 ? safe : 1, fraud];
        riskChartInstance.update();

        trendData.shift(); 
        trendData.push(rate); 
        trendChartInstance.update();

    } catch (error) {
        console.error("Failed to fetch metrics:", error);
    }
}

async function submitTransaction() {
    const btnText = document.getElementById('btnText');
    const btnSpinner = document.getElementById('btnSpinner');
    const amount = parseFloat(document.getElementById('txAmount').value) || 0;

    btnText.classList.add('hidden');
    btnSpinner.classList.remove('hidden');

    const isFraud = Math.random() > 0.5;
    let payload = {};

    if (isFraud) {
        payload = {
            "Time": Date.now() % 100000, "Amount": amount, "V1": -2.3122, "V2": 1.9519, "V3": -1.6098, "V4": 3.9979, 
            "V5": -0.5221, "V6": -1.4265, "V7": -2.5373, "V8": 1.3916, "V9": -2.7700, "V10": -2.7722, 
            "V11": 3.2020, "V12": -2.8999, "V13": -0.5952, "V14": -4.2892, "V15": 0.3897, "V16": -1.1407, 
            "V17": -2.8300, "V18": -0.0168, "V19": 0.4169, "V20": 0.1269, "V21": 0.5172, "V22": -0.0350, 
            "V23": -0.4652, "V24": 0.3201, "V25": 0.0445, "V26": 0.1778, "V27": 0.2611, "V28": -0.1432
        };
    } else {
        payload = {
            "Time": Date.now() % 100000, "Amount": amount, "V1": 1.1918, "V2": 0.2661, "V3": 0.1664, "V4": 0.4481, 
            "V5": 0.0600, "V6": -0.0823, "V7": -0.0788, "V8": 0.0851, "V9": -0.2554, "V10": -0.1669, 
            "V11": 1.6127, "V12": 1.0652, "V13": 0.4890, "V14": -0.1437, "V15": 0.6355, "V16": 0.4639, 
            "V17": -0.1148, "V18": -0.1833, "V19": -0.1457, "V20": -0.0690, "V21": -0.2257, "V22": -0.6386, 
            "V23": 0.1012, "V24": -0.3398, "V25": 0.1671, "V26": 0.1258, "V27": -0.0089, "V28": 0.0147
        };
    }

    try {
        const start = performance.now();
        const response = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-API-KEY': API_KEY // Added Security Header
            },
            body: JSON.stringify(payload)
        });
        const end = performance.now();
        document.getElementById('kpiLatency').innerText = `${Math.round(end - start)}ms`;

        if (response.status === 429) {
            alert("Rate Limit Exceeded! Please slow down.");
            return;
        }

        const data = await response.json();
        updateResultUI(data);
        updateTable(data, amount);
        fetchMetrics(); 
        
    } catch (error) {
        alert("API Connection Error. Ensure Docker is running.");
    } finally {
        btnSpinner.classList.add('hidden');
        btnText.classList.remove('hidden');
    }
}

function updateResultUI(data) {
    const card = document.getElementById('resultCard');
    const actionEl = document.getElementById('resAction');
    const badgeEl = document.getElementById('resBadge');
    const probBar = document.getElementById('probBar');
    
    card.classList.remove('hidden');
    document.getElementById('resId').innerText = data.transaction_id;
    actionEl.innerText = data.action;
    document.getElementById('resProb').innerText = (data.fraud_probability * 100).toFixed(2) + '%';

    let colorClass, bgClass;
    if (data.risk_level === 'HIGH') {
        colorClass = 'text-red-500'; bgClass = 'bg-red-500';
        card.className = "bg-red-900/20 border border-red-500/50 p-6 rounded-2xl shadow-[0_0_30px_rgba(239,68,68,0.2)] transition-all";
        badgeEl.className = "px-3 py-1 text-xs font-bold rounded-full bg-red-500/20 text-red-400";
    } else if (data.risk_level === 'MEDIUM') {
        colorClass = 'text-yellow-500'; bgClass = 'bg-yellow-500';
        card.className = "bg-yellow-900/20 border border-yellow-500/50 p-6 rounded-2xl shadow-[0_0_30px_rgba(234,179,8,0.2)] transition-all";
        badgeEl.className = "px-3 py-1 text-xs font-bold rounded-full bg-yellow-500/20 text-yellow-400";
    } else {
        colorClass = 'text-green-500'; bgClass = 'bg-green-500';
        card.className = "bg-green-900/20 border border-green-500/50 p-6 rounded-2xl shadow-[0_0_30px_rgba(34,197,94,0.2)] transition-all";
        badgeEl.className = "px-3 py-1 text-xs font-bold rounded-full bg-green-500/20 text-green-400";
    }

    actionEl.className = `text-2xl font-bold ${colorClass}`;
    badgeEl.innerText = `${data.risk_level} RISK`;
    
    probBar.className = `h-2.5 rounded-full transition-all duration-1000 ${bgClass}`;
    setTimeout(() => { probBar.style.width = `${data.fraud_probability * 100}%`; }, 100);
}

function updateTable(data, amount) {
    localTransactionHistory.unshift({ ...data, amount });
    if (localTransactionHistory.length > 10) localTransactionHistory.pop();

    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';

    localTransactionHistory.forEach(tx => {
        let actionColor = tx.action === 'BLOCK' ? 'text-red-400 bg-red-400/10' : 
                          tx.action === 'REVIEW_REQUIRED' ? 'text-yellow-400 bg-yellow-400/10' : 
                          'text-green-400 bg-green-400/10';

        const row = `<tr class="hover:bg-slate-700/30 transition-colors">
            <td class="px-6 py-4 font-mono text-xs">#${tx.transaction_id} <span class="text-slate-600">v${tx.model_version}</span></td>
            <td class="px-6 py-4">$${amount.toFixed(2)}</td>
            <td class="px-6 py-4">${(tx.fraud_probability * 100).toFixed(2)}%</td>
            <td class="px-6 py-4"><span class="px-2 py-1 rounded text-xs font-bold ${actionColor}">${tx.action}</span></td>
        </tr>`;
        tbody.innerHTML += row;
    });
}

window.onload = () => {
    initCharts();
    fetchMetrics();
    setInterval(fetchMetrics, 10000); 
};
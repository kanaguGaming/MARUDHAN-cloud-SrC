document.addEventListener("DOMContentLoaded", () => {
    const dataLog = document.getElementById("data-log");
    
    function appendLog(message, type="data-msg") {
        const p = document.createElement("p");
        p.className = type;
        const time = new Date().toLocaleTimeString();
        p.innerText = `[${time}] ${message}`;
        dataLog.appendChild(p);
        dataLog.scrollTop = dataLog.scrollHeight;
    }

    async function fetchLatestData() {
        try {
            const response = await fetch('/api/digital_twin/latest');
            const result = await response.json();
            
            if (result.data && result.data.length > 0) {
                const latest = result.data[0];
                
                // Update stats
                if(latest.temperature_c !== null && latest.temperature_c !== undefined) {
                    document.getElementById('temp-val').innerText = `${latest.temperature_c.toFixed(1)} °C`;
                }
                if(latest.humidity_percent !== null && latest.humidity_percent !== undefined) {
                    document.getElementById('hum-val').innerText = `${latest.humidity_percent.toFixed(1)} %`;
                }
                if(latest.soil_moisture_percent !== null && latest.soil_moisture_percent !== undefined) {
                    document.getElementById('soil-val').innerText = `${latest.soil_moisture_percent.toFixed(1)} %`;
                }

                // Update ARIVU
                if (latest.arivu_analysis) {
                    const healthEl = document.getElementById('health-val');
                    healthEl.innerText = latest.arivu_analysis.crop_health_status;
                    healthEl.style.color = latest.arivu_analysis.crop_health_status === 'Optimal' ? '#00ff88' : '#ff4757';
                    
                    document.getElementById('rec-val').innerText = latest.arivu_analysis.ai_recommendation;
                }

                appendLog(`Received update from ${latest.device_id}`);
            }
        } catch (error) {
            console.error("Error fetching data:", error);
            appendLog("Connection to Digital Twin lost. Retrying...", "sys-msg");
        }
    }

    // Initial fetch
    fetchLatestData();
    
    // Poll every 5 seconds (simulating real-time connection for now)
    setInterval(fetchLatestData, 5000);
});

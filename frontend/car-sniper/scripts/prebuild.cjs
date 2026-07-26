const fs = require('fs');
const path = require('path');
const API_BASE = process.env.VITE_API_URL || 'https://motorbit.vercel.app';

async function fetchData() {
    const initialData = { deals: [], stats: {} };
    try {
        const dealsRes = await fetch(`${API_BASE}/api/deals/top`);
        if (dealsRes.ok) { const j = await dealsRes.json(); initialData.deals = j.results || []; }
    } catch (e) { console.log('Deals fetch skipped'); }
    try {
        const statsRes = await fetch(`${API_BASE}/api/site/stats`);
        if (statsRes.ok) { initialData.stats = await statsRes.json(); }
    } catch (e) { console.log('Stats fetch skipped'); }
    fs.writeFileSync(path.join(__dirname, '..', 'public', 'initial-data.json'), JSON.stringify(initialData));
    console.log(`Preloaded ${initialData.deals.length} deals`);
}
fetchData();

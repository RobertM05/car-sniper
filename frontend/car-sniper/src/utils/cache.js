const CACHE_PREFIX = 'motorbit_cache_';
const DEFAULT_TTL = 300000; // 5 minutes

export function getCached(key) {
    try {
        const entry = JSON.parse(localStorage.getItem(CACHE_PREFIX + key));
        if (!entry) return null;
        if (Date.now() - entry.timestamp > (entry.ttl || DEFAULT_TTL)) {
            localStorage.removeItem(CACHE_PREFIX + key);
            return null;
        }
        return entry.data;
    } catch {
        return null;
    }
}

export function setCache(key, data, ttl = DEFAULT_TTL) {
    try {
        localStorage.setItem(CACHE_PREFIX + key, JSON.stringify({
            data,
            timestamp: Date.now(),
            ttl,
        }));
    } catch {
        // localStorage full — ignore
    }
}

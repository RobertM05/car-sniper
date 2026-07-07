const HISTORY_KEY = 'carsniper_search_history';
const MAX_HISTORY = 10;

export function getSearchHistory() {
    try {
        return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
    } catch {
        return [];
    }
}

export function addSearchHistory(search) {
    const history = getSearchHistory();
    const filtered = history.filter(
        h => !(h.make === search.make && h.model === search.model)
    );
    filtered.unshift({ ...search, timestamp: Date.now() });
    localStorage.setItem(HISTORY_KEY, JSON.stringify(filtered.slice(0, MAX_HISTORY)));
}

export function clearSearchHistory() {
    localStorage.removeItem(HISTORY_KEY);
}

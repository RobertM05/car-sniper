# Car Sniper

Car Sniper is a high-performance, real-time car search aggregator designed to unify listing data from major platforms (OLX, Autovit) into a single, cohesive interface. It features advanced data normalization, validation, and automated repair logic to ensure data accuracy.

## key Features

### 1. Unified Search Engine
- **Aggregated Results**: Fetches data concurrently from multiple sources using asynchronous I/O.
- **Normalization**: Standardizes prices, dates, and vehicle specifications across different platforms.
- **Deduplication**: Automatically identifies and merges duplicate listings based on unique platform identifiers.

### 2. Live Data Validation (Auto-Repair)
The system implements a robust validation layer that intercepts search results in real-time:
- **Missing Asset Recovery**: Detects listings with missing images and performs a deep-fetch to recover them from meta tags, JSON-LD schema, or gallery selectors.
- **Price Verification**: Correlates the displayed price with the internal structured data of the source page to correct parsing errors (e.g., correcting 9,000 EUR to 91,000 EUR for luxury vehicles).
- **Stale Data Pruning**: Automatically filters out listings that return 404 errors or redirects, ensuring only active ads are displayed.

### 3. Performance
- **Asynchronous Architecture**: Built on Python `asyncio` and `aiohttp` for non-blocking network operations.
- **In-Memory Caching**: Implements LRU caching for search queries to reduce latency for repeated requests.
- **Optimized Frontend**: React-based UI with efficient state management and responsive design.

## Technical Stack

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Scraping**: Aiohttp, BeautifulSoup4
- **Database**: SQLite (for persistent configuration and analytics)
- **Utilities**: Pydantic for data validation

### Frontend
- **Framework**: React.js (Vite)
- **Styling**: Modern CSS3 with responsive layouts
- **State Management**: React Hooks

## Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 16 or higher

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd car-sniper
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cd ..
   ```

3. **Frontend Setup**
   ```bash
   cd frontend/car-sniper
   npm install
   cd ../..
   ```

## Usage

The project includes a unified startup script for convenience.

1. **Start the Application**
   ```bash
   ./start.sh
   ```
   This command will:
   - Launch the FastAPI backend on port 8000.
   - Launch the React frontend development server on port 5173.

2. **Access the Interface**
   Open your browser and navigate to `http://localhost:5173`.

## Configuration

Environment variables and secrets are managed via `.env` files (not included in version control).

### Important Note on Scrapers
The scraping modules are designed to respect rate limits. The `start.sh` script is currently configured to run in "Live Search Mode" (Direct Scraping) for maximum data freshness. Background crawling features can be enabled by uncommenting the relevant section in `start.sh`.

## License
Proprietary software. All rights reserved.

# Generador de Quinielas Progol

## Overview

This is a Streamlit-based web application that generates random lottery tickets (quinielas) for Progol, a Mexican sports betting game operated by Lotería Nacional. The application scrapes current match data from the official Lotería Nacional website, generates random predictions for soccer matches, stores historical data in PostgreSQL, and exports predictions as shareable images.

The system helps users create lottery tickets by automatically fetching current Progol matches and generating randomized predictions (Local/Home win, Draw, or Visitante/Away win) for up to 14 matches per ticket.

**Latest Update (October 2025)**: Enhanced with historical tracking, intelligent generation modes, prize/sorteo information display, and PNG image export functionality.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

### October 16, 2025 - Major Feature Release
- ✅ **Database Integration**: Added PostgreSQL persistence for quiniela history
- ✅ **Historical View**: Users can view, download, and delete previously generated quinielas
- ✅ **Image Export**: PNG export with professional Progol branding design
- ✅ **Sorteo Information**: Real-time display of prize amounts, draw dates, and jornada numbers
- ✅ **Intelligent Generation**: Added weighted prediction mode favoring home team wins
- ✅ **Error Handling**: Robust handling of database unavailability and scraping failures

## System Architecture

### Frontend Architecture
**Technology**: Streamlit web framework
- Single-page application with session state management
- Responsive layout using Streamlit's column-based grid system
- Sidebar for configuration controls with dual view selector (Generate / History)
- Real-time display of lottery draw information (date, prizes, round)
- Support for multiple views: generation, history, and export functionality

**Design Pattern**: Session-based state management
- All core components (scraper, generator, database, exporter) initialized once in `st.session_state`
- Persistent data stored across user interactions within the session
- Avoids redundant object instantiation and API calls
- Graceful degradation when database is unavailable

### Backend Architecture
**Core Components**:

1. **Web Scraper** (`scraper.py` - PrognolScraper)
   - Primary: Uses `requests` + `BeautifulSoup` for HTML parsing
   - Fallback: Uses `trafilatura` library for content extraction
   - Graceful degradation: Returns sample matches if scraping fails
   - **NEW**: `get_info_sorteo()` method extracts prize info, draw dates, jornada numbers
   - Intelligent fallback: Calculates next Sunday for draw dates when scraping fails
   - Caches lottery information to minimize requests
   - Implements retry logic and timeout handling

2. **Prediction Generator** (`quiniela_generator.py` - QuinielaGenerator)
   - Pure Python random prediction engine
   - Supports three outcomes: Local (1), Empate/Draw (X), Visitante (2)
   - Batch generation capability for multiple tickets
   - **NEW**: `generar_quiniela_con_tendencia()` for weighted predictions
   - Intelligent mode: 50% local, 25% empate, 25% visitante (statistically favors home teams)
   - Limited to 14 matches per ticket (Progol standard)

3. **Image Exporter** (`image_exporter.py` - QuinielaImageExporter)
   - Uses PIL (Pillow) for PNG image generation
   - Progol branding colors: Verde #2E8B57, white, light gray
   - Fixed width (800px) with dynamic height based on match count
   - Visual sections: branded header, match rows with alternating backgrounds, summary footer
   - Returns image as bytes for immediate download
   - Unique filenames with timestamp to prevent conflicts

4. **Database Manager** (`database.py` - QuinielaDatabase)
   - PostgreSQL connection via psycopg2
   - `db_available` flag for graceful operation without database
   - Auto-initialization: Creates tables and indexes on first connection
   - Methods: `guardar_quiniela`, `obtener_quinielas`, `eliminar_quiniela`, `obtener_estadisticas`
   - JSON parsing safeguards for JSONB data retrieval
   - Comprehensive error handling with safe defaults

### Data Storage Solutions
**Database**: PostgreSQL with psycopg2 driver
- Connection managed via `DATABASE_URL` environment variable
- **Graceful handling**: Application fully functional even when database is unavailable
- Schema: Single `quinielas` table with JSONB column for flexible data storage
- Auto-initialization: Creates tables and indexes on first connection
- Indexed by generation timestamp (DESC) for efficient historical queries

**Schema Design**:
```sql
CREATE TABLE quinielas (
  id SERIAL PRIMARY KEY,
  fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  num_partidos INTEGER,
  datos JSONB NOT NULL
);

CREATE INDEX idx_quinielas_fecha ON quinielas(fecha_generacion DESC);
```

**Rationale**: JSONB chosen for flexibility as prediction structure may evolve. Indexed timestamp supports efficient "recent tickets" queries. The `db_available` pattern allows the app to work seamlessly in environments without PostgreSQL.

### User Interface Features

**Main View (Generar Quinielas)**:
- Information cards: Draw date, jornada number, prize amounts
- Left panel: Current matches with team names and dates
- Right panel: Generated quinielas with expandable sections
- Each quiniela shows: DataFrame table, prediction summary, download button
- Controls: Match update, quantity selector (1/5/10), mode selector, generate button

**History View (Historial)**:
- List of all saved quinielas with ID and timestamp
- Statistics sidebar: Total quinielas count
- Actions per quiniela: Download as PNG, Delete
- Expandable sections showing full prediction details
- Auto-refresh capability

**Generation Modes**:
1. **Aleatorio (Random)**: Completely random predictions across all outcomes
2. **Inteligente (Intelligent)**: Weighted towards home team wins
   - 50% probability: Local wins
   - 25% probability: Empate (Draw)
   - 25% probability: Visitante wins
   - Based on statistical home advantage in soccer

### External Dependencies

**Web Scraping**:
- **Lotería Nacional Website** (`lotenal.gob.mx/ESM/progol.html`)
  - Source of current Progol matches and lottery draw information
  - Scraped using HTTP requests with user-agent spoofing
  - No authentication required (public data)
  - Multiple regex patterns for robust data extraction

**Python Libraries**:
- `streamlit` - Web application framework
- `pandas` - Data manipulation (match and prediction data)
- `requests` + `BeautifulSoup4` - Primary web scraping
- `trafilatura` - Fallback content extraction
- `Pillow (PIL)` - Image generation for ticket exports
- `psycopg2-binary` - PostgreSQL database driver
- `reportlab` - PDF generation capabilities (future enhancement)

**Database**:
- PostgreSQL instance (via DATABASE_URL environment variable)
- Optional dependency - application works in degraded mode without database
- Used for persistent storage of historical predictions
- Environment variables: DATABASE_URL, PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE

**Configuration**:
- Environment variables: `DATABASE_URL` for PostgreSQL connection
- No API keys or authentication tokens required for Progol scraping
- All external data access is from public sources
- Streamlit server configuration in `.streamlit/config.toml`

### File Structure
```
.
├── app.py                    # Main Streamlit application
├── scraper.py               # Web scraper for Progol data
├── quiniela_generator.py    # Prediction generation logic
├── database.py              # PostgreSQL persistence layer
├── image_exporter.py        # PNG image export functionality
├── .streamlit/
│   └── config.toml          # Streamlit server configuration
└── replit.md                # This documentation file
```

### Error Handling & Resilience

**Database Unavailability**:
- All database methods check `db_available` flag before operations
- Returns safe defaults (empty lists, None, zero counts) when DB is unavailable
- User sees quinielas in current session even without persistence
- No crashes or exceptions when DATABASE_URL is missing

**Web Scraping Failures**:
- Primary scraping with BeautifulSoup, fallback to Trafilatura
- Ultimate fallback: Generates realistic sample matches from known teams
- Sorteo info extraction uses multiple regex patterns
- Intelligent defaults: Calculates next Sunday for draw dates

**Session State Management**:
- All components initialized before first access
- Proper initialization order prevents AttributeError
- Cached sorteo information to reduce redundant requests

### Testing & Validation

**End-to-End Testing (October 16, 2025)**:
- ✅ Homepage loads with title and info panels
- ✅ Match update fetches 14 partidos successfully
- ✅ Random generation creates quinielas with proper table structure
- ✅ Intelligent mode generates with weighted probabilities
- ✅ Image download produces PNG files with unique names
- ✅ History view displays saved quinielas
- ✅ Delete functionality removes quinielas from database
- ✅ View switching works correctly between Generate and History

**Known Minor Issues**:
- SSL certificate warnings during scraping (handled with retries)
- Streamlit deprecation warning for `use_container_width` (cosmetic)
- PIL type hints in LSP (does not affect functionality)

### Future Enhancements (Suggested)

1. **Advanced Analytics**: Track prediction accuracy over time
2. **PDF Export**: Alternative to PNG for printing
3. **Social Sharing**: Direct share to WhatsApp/Facebook
4. **User Accounts**: Personal history and preferences
5. **Statistical Analysis**: Show historical win patterns
6. **Mobile Optimization**: Enhanced responsive design
7. **Multi-language Support**: English and Spanish interfaces

```
                        ███╗   ███╗███╗   ██╗███████╗
                        ████╗ ████║████╗  ██║██╔════╝
                        ██╔████╔██║██╔██╗ ██║███████╗
                        ██║╚██╔╝██║██║╚██╗██║╚════██║
                        ██║ ╚═╝ ██║██║ ╚████║███████║
                        ╚═╝     ╚═╝╚═╝  ╚═══╝╚══════╝            

                        # Monitor New Subdomain
                        # @omarelfarsaoui
                        # version 2.0.0     
```
# Professional Subdomain Monitor

A production-ready subdomain monitoring system with both API and CLI interfaces.

## Features

- 🔍 Automatic subdomain discovery from multiple sources (crt.sh, ThreatMiner)
- 🔔 Real-time notifications (Slack, Telegram)
- 🌐 RESTful API with FastAPI
- 💻 Powerful CLI for automation
- 📊 MongoDB storage with async operations
- 🐳 Docker support for easy deployment
- 🧪 Comprehensive test coverage

## Quick Start

### Using Docker (Recommended)

```bash
# Start services
docker-compose up -d

# API will be available at http://localhost:8000
# MongoDB at localhost:27017
```

### Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your settings
nano .env

# Start API
uvicorn src.api.main:app --reload

# Or use CLI
python cli.py --help
```

## API Usage

### Add Domain
```bash
curl -X POST "http://localhost:8000/api/v1/domains" \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com", "notify_slack": true}'
```

### List Domains
```bash
curl "http://localhost:8000/api/v1/domains"
```

### Get Subdomains
```bash
curl "http://localhost:8000/api/v1/domains/example.com/subdomains"
```

### Trigger Monitoring
```bash
curl -X POST "http://localhost:8000/api/v1/monitoring/check-all"
```

### Get Statistics
```bash
curl "http://localhost:8000/api/v1/monitoring/stats"
```

## CLI Usage

### Add single domain
```bash
python cli.py --add example.com --slack --telegram
```

### Import from file
```bash
python cli.py --import-file domains.txt
```

### List all domains
```bash
python cli.py --list-domains
```

### List subdomains for domain
```bash
python cli.py --list-subdomains example.com
```

### Run monitoring
```bash
python cli.py --monitor
```

### Export all subdomains
```bash
python cli.py --export
```

### Delete domain
```bash
python cli.py --delete example.com
```

## Configuration

Edit `.env` file:

```env
# Database
DB_HOST=localhost
DB_PORT=27017
DB_NAME=subdomain_monitor

# Notifications
SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Monitoring
MONITOR_INTERVAL_MINUTES=60
MAX_WORKERS=10
```

## API Documentation

Visit http://localhost:8000/docs for interactive API documentation (Swagger UI).

Visit http://localhost:8000/redoc for ReDoc documentation.

## Architecture

```
┌─────────────┐
│   FastAPI   │
│     API     │
└──────┬──────┘
       │
┌──────▼──────────────┐
│  Monitoring Service │
│  (Business Logic)   │
└──────┬──────────────┘
       │
┌──────▼──────────┐
│   Repository    │
│  (MongoDB I/O)  │
└──────┬──────────┘
       │
┌──────▼──────┐
│   MongoDB   │
└─────────────┘
```

## Development

### Run tests
```bash
pytest tests/ -v
```

### Code formatting
```bash
black src/
isort src/
```

### Type checking
```bash
mypy src/
```

## Production Deployment

### With Docker
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### With systemd
Create `/etc/systemd/system/subdomain-monitor.service`:

```ini
[Unit]
Description=Subdomain Monitor API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/subdomain-monitor
Environment="PATH=/opt/subdomain-monitor/venv/bin"
ExecStart=/opt/subdomain-monitor/venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable subdomain-monitor
sudo systemctl start subdomain-monitor
```

## Scheduled Monitoring

The API includes an integrated scheduler that can automatically monitor all domains at regular intervals.

### Enable Scheduler

In your `.env` file:
```env
ENABLE_SCHEDULER=true
MONITOR_INTERVAL_MINUTES=60  # Check every 60 minutes
SCHEDULER_TIMEZONE=UTC
```

Then restart the API:
```bash
uvicorn src.api.main:app --reload
```

### Scheduler API Endpoints

#### Get Scheduler Status
```bash
curl "http://localhost:8000/api/v1/scheduler/status"
```

Response:
```json
{
  "enabled": true,
  "running": true,
  "interval_minutes": 60,
  "timezone": "UTC",
  "next_run": "2026-01-01T15:00:00",
  "current_time": "2026-01-01T14:23:45"
}
```

#### List Scheduled Jobs
```bash
curl "http://localhost:8000/api/v1/scheduler/jobs"
```

#### Manually Trigger Monitoring Now
```bash
curl -X POST "http://localhost:8000/api/v1/scheduler/trigger"
```

#### Pause Scheduler
```bash
curl -X POST "http://localhost:8000/api/v1/scheduler/pause"
```

#### Resume Scheduler
```bash
curl -X POST "http://localhost:8000/api/v1/scheduler/resume"
```

### How It Works

1. **Automatic Monitoring**: When enabled, the scheduler runs `monitor_all_domains()` at the configured interval
2. **No Overlaps**: The scheduler prevents overlapping runs (max 1 instance)
3. **Missed Runs**: If a run is missed (e.g., server restart), it combines them into one
4. **Grace Period**: 5-minute grace period for delayed starts
5. **Logging**: All runs are logged with detailed statistics

### Monitoring Intervals

Choose based on your needs:
- **Every 5 minutes**: `MONITOR_INTERVAL_MINUTES=5` (High frequency, more API calls)
- **Every hour**: `MONITOR_INTERVAL_MINUTES=60` (Recommended for most use cases)
- **Every 6 hours**: `MONITOR_INTERVAL_MINUTES=360` (Low frequency)
- **Daily**: `MONITOR_INTERVAL_MINUTES=1440` (Once per day)

### View Logs

```bash
# Docker
docker-compose logs -f api
```

You'll see:
```
2026-01-01 14:00:00 - INFO - ============================================================
2026-01-01 14:00:00 - INFO - Starting scheduled monitoring job at 2026-01-01 14:00:00
2026-01-01 14:00:00 - INFO - ============================================================
2026-01-01 14:05:23 - INFO - Scheduled monitoring completed:
2026-01-01 14:05:23 - INFO -   - Domains monitored: 15
2026-01-01 14:05:23 - INFO -   - New subdomains found: 3
2026-01-01 14:05:23 - INFO -   - Errors: 0
```

### Alternative: Using Cron

If you prefer not to use the built-in scheduler, you can use cron instead:

```bash
# Edit crontab
crontab -e

# Add (runs every hour)
0 * * * * cd /path/to/project && /path/to/python cli.py --monitor

# Or use curl to trigger API endpoint
0 * * * * curl -X POST http://localhost:8000/api/v1/monitoring/check-all
```

## License

Do whatever you want with this code.

## Contributing

Pull requests are welcome!

## Feedback and issues
***[Create new issue](https://github.com/elfarsaouiomar/monitor-new-subdomain/issues/new)***

## inspired from https://github.com/yassineaboukir/sublert

### Todo
 * ~~add output file~~
 * ~~add Docker~~
 * Add snyk
 * add more subdomain resources
    * ~~Certspotter~~
    * Virustotal
    * ~~Sublist3r~~
    * Facebook **
    * Spyse (CertDB) *
    * Bufferover
    * Threatcrowd
    * Virustotal with apikey **
    * AnubisDB
    * Urlscan.io
    * SecurityTrails **
    * ~~Threatminer~~

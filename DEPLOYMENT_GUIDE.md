# 🚀 راهنمای استقرار سیستم ربات آموزش زبان انگلیسی

## 📋 فهرست مطالب

1. [پیش‌نیازهای سیستم](#پیشنیازهای-سیستم)
2. [تنظیمات اولیه](#تنظیمات-اولیه)
3. [استقرار محلی (Local)](#استقرار-محلی-local)
4. [استقرار Cloud (AWS/DigitalOcean)](#استقرار-cloud-awsdigitalocean)
5. [Docker Deployment](#docker-deployment)
6. [مانیتورینگ و Logging](#مانیتورینگ-و-logging)
7. [Backup و Recovery](#backup-و-recovery)
8. [بهینه‌سازی Performance](#بهینهسازی-performance)
9. [امنیت](#امنیت)
10. [عیب‌یابی](#عیبیابی)

---

## 💻 پیش‌نیازهای سیستم

### سخت‌افزار (حداقل)
- **CPU:** 1 core (2+ پیشنهادی)
- **RAM:** 512MB (1GB+ پیشنهادی)
- **Storage:** 2GB فضای خالی
- **Network:** اتصال پایدار به اینترنت

### نرم‌افزار
- **OS:** Linux (Ubuntu 20.04+), Windows 10+, macOS 10.15+
- **Python:** 3.9 یا بالاتر
- **Git:** برای clone کردن پروژه
- **SQLite:** 3.31+ (معمولاً با Python نصب می‌شود)

### حساب‌های خارجی
- **Telegram Bot Token:** از [@BotFather](https://t.me/botfather)
- **OpenAI API Key:** از [OpenAI Platform](https://platform.openai.com)

---

## ⚙️ تنظیمات اولیه

### 1. دریافت Telegram Bot Token

```bash
# 1. به @BotFather در تلگرام پیام دهید
# 2. دستور /newbot را ارسال کنید
# 3. نام و username ربات را تعیین کنید
# 4. Token دریافتی را یادداشت کنید

# مثال Token:
# 1234567890:ABCdefGHijklMNopQRstUVwXYz
```

### 2. دریافت OpenAI API Key

```bash
# 1. به https://platform.openai.com وارد شوید
# 2. بخش API Keys را باز کنید
# 3. Create new secret key کلیک کنید
# 4. Key را کپی و در جای امن ذخیره کنید

# مثال Key:
# sk-proj-abc123def456ghi789...
```

### 3. بررسی اعتبار (Credit) OpenAI

```bash
# بررسی اعتبار موجود
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.openai.com/v1/usage

# حداقل $5 credit توصیه می‌شود
```

---

## 🏠 استقرار محلی (Local)

### مرحله 1: دانلود پروژه

```bash
# Clone کردن پروژه
git clone https://github.com/your-repo/english-learning-bot.git
cd english-learning-bot

# یا دانلود مستقیم فایل‌ها
# اگر پروژه روی سیستم محلی است
cd /path/to/telegram_bot
```

### مرحله 2: تنظیم محیط Python

```bash
# ایجاد virtual environment
python -m venv venv

# فعال‌سازی (Linux/Mac)
source venv/bin/activate

# فعال‌سازی (Windows)
venv\Scripts\activate

# بررسی نسخه Python
python --version  # باید 3.9+ باشد
```

### مرحله 3: نصب Dependencies

```bash
# نصب پکیج‌های مورد نیاز
pip install --upgrade pip
pip install python-telegram-bot==20.3
pip install openai
pip install python-dotenv

# یا استفاده از requirements.txt
pip install -r requirements.txt
```

### مرحله 4: تنظیم متغیرهای محیطی

```bash
# ایجاد فایل .env
cat > .env << EOF
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
EOF

# تنظیم دسترسی فایل
chmod 600 .env
```

### مرحله 5: تست و اجرا

```bash
# تست اتصال به OpenAI
python -c "
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
response = client.chat.completions.create(
    model='gpt-3.5-turbo',
    messages=[{'role': 'user', 'content': 'Test'}],
    max_tokens=10
)
print('OpenAI connection successful!')
"

# اجرای ربات
python bot.py
```

### مرحله 6: تست ربات

```bash
# 1. ربات را در تلگرام پیدا کنید (@your_bot_username)
# 2. دستور /start را ارسال کنید
# 3. آزمون تعیین سطح را انجام دهید
# 4. قابلیت‌های مختلف را تست کنید
```

---

## ☁️ استقرار Cloud (AWS/DigitalOcean)

### AWS EC2 Deployment

#### 1. ایجاد EC2 Instance

```bash
# Launch EC2 instance با:
# - AMI: Ubuntu 20.04 LTS
# - Instance Type: t2.micro (Free tier)
# - Security Group: SSH (22), Custom (8443 for webhook)
# - Key Pair: ایجاد یا انتخاب کلید موجود
```

#### 2. اتصال به Server

```bash
# اتصال SSH
ssh -i your-key.pem ubuntu@your-ec2-public-ip

# به‌روزرسانی سیستم
sudo apt update && sudo apt upgrade -y

# نصب Python و Git
sudo apt install python3 python3-pip python3-venv git -y
```

#### 3. Setup پروژه روی Server

```bash
# Clone پروژه
git clone https://github.com/your-repo/english-learning-bot.git
cd english-learning-bot

# ایجاد virtual environment
python3 -m venv venv
source venv/bin/activate

# نصب dependencies
pip install -r requirements.txt

# تنظیم .env
nano .env
# محتوا:
# TELEGRAM_BOT_TOKEN=your_token
# OPENAI_API_KEY=your_key
```

#### 4. تنظیم Systemd Service

```bash
# ایجاد service file
sudo nano /etc/systemd/system/telegram-bot.service

# محتوا:
[Unit]
Description=English Learning Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/english-learning-bot
Environment=PATH=/home/ubuntu/english-learning-bot/venv/bin
ExecStart=/home/ubuntu/english-learning-bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 5. فعال‌سازی Service

```bash
# reload daemon
sudo systemctl daemon-reload

# فعال‌سازی service
sudo systemctl enable telegram-bot.service

# شروع service
sudo systemctl start telegram-bot.service

# بررسی وضعیت
sudo systemctl status telegram-bot.service

# مشاهده logs
sudo journalctl -u telegram-bot.service -f
```

### DigitalOcean Droplet

#### 1. ایجاد Droplet

```bash
# از پنل DigitalOcean:
# - Ubuntu 20.04 LTS
# - Basic plan ($6/month)
# - Add SSH key
# - Enable monitoring
```

#### 2. تنظیمات اولیه

```bash
# اتصال به droplet
ssh root@your-droplet-ip

# ایجاد کاربر جدید
adduser botuser
usermod -aG sudo botuser

# تنظیم SSH برای کاربر جدید
mkdir /home/botuser/.ssh
cp ~/.ssh/authorized_keys /home/botuser/.ssh/
chown -R botuser:botuser /home/botuser/.ssh
chmod 700 /home/botuser/.ssh
chmod 600 /home/botuser/.ssh/authorized_keys

# اتصال با کاربر جدید
ssh botuser@your-droplet-ip
```

#### 3. نصب و تنظیم

```bash
# همان مراحل AWS EC2 را دنبال کنید
# فقط paths ممکن است متفاوت باشد:
# /home/botuser/english-learning-bot
```

---

## 🐳 Docker Deployment

### 1. ایجاد Dockerfile

```dockerfile
# ایجاد Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create volume for database
VOLUME ["/app/data"]

# Environment variables
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "bot.py"]
EOF
```

### 2. ایجاد docker-compose.yml

```yaml
# ایجاد docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  telegram-bot:
    build: .
    container_name: english-learning-bot
    restart: unless-stopped
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    env_file:
      - .env
    networks:
      - bot-network

networks:
  bot-network:
    driver: bridge

volumes:
  bot-data:
EOF
```

### 3. Build و Run

```bash
# Build image
docker build -t english-learning-bot .

# Run با docker-compose
docker-compose up -d

# مشاهده logs
docker-compose logs -f

# Stop
docker-compose down

# Stop و remove volumes
docker-compose down -v
```

### 4. Docker در Production

```bash
# تنظیم automatic restart
docker run -d \
  --name english-learning-bot \
  --restart unless-stopped \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  english-learning-bot

# Health check
docker ps
docker logs english-learning-bot

# Update کردن
docker stop english-learning-bot
docker rm english-learning-bot
docker build -t english-learning-bot .
# سپس run مجدد
```

---

## 📊 مانیتورینگ و Logging

### 1. تنظیم Logging

```python
# ایجاد فایل logging_config.py
import logging
import logging.handlers
import os

def setup_logging():
    # ایجاد پوشه logs
    os.makedirs('logs', exist_ok=True)
    
    # تنظیم formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler با rotation
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/bot.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Error log جداگانه
    error_handler = logging.handlers.RotatingFileHandler(
        'logs/errors.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

# در bot.py اضافه کنید:
from logging_config import setup_logging
setup_logging()
```

### 2. Monitoring Script

```bash
# ایجاد monitoring.sh
cat > monitoring.sh << 'EOF'
#!/bin/bash

LOGFILE="logs/monitor.log"
BOT_PID=$(pgrep -f "python bot.py")

echo "$(date): Checking bot status..." >> $LOGFILE

if [ -z "$BOT_PID" ]; then
    echo "$(date): Bot is not running! Restarting..." >> $LOGFILE
    cd /path/to/telegram_bot
    source venv/bin/activate
    nohup python bot.py > logs/bot_output.log 2>&1 &
    echo "$(date): Bot restarted" >> $LOGFILE
else
    echo "$(date): Bot is running (PID: $BOT_PID)" >> $LOGFILE
fi

# بررسی فضای disk
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    echo "$(date): WARNING: Disk usage is ${DISK_USAGE}%" >> $LOGFILE
fi

# بررسی memory
MEM_USAGE=$(free | awk 'NR==2{printf "%.1f", $3*100/$2 }')
if (( $(echo "$MEM_USAGE > 90" | bc -l) )); then
    echo "$(date): WARNING: Memory usage is ${MEM_USAGE}%" >> $LOGFILE
fi
EOF

chmod +x monitoring.sh
```

### 3. Cron Job برای Monitoring

```bash
# اضافه کردن به crontab
crontab -e

# اضافه کردن خط زیر (هر 5 دقیقه چک کند):
*/5 * * * * /path/to/telegram_bot/monitoring.sh

# روزانه backup (ساعت 2 صبح):
0 2 * * * /path/to/telegram_bot/backup.sh
```

### 4. Log Analysis

```bash
# نمایش آخرین errors
tail -50 logs/errors.log

# جستجو برای خطاهای خاص
grep "OpenAI" logs/bot.log | tail -20

# تحلیل آمار استفاده
cat logs/bot.log | grep "User.*started" | wc -l

# نمایش Active users امروز
grep "$(date +%Y-%m-%d)" logs/bot.log | grep "User.*started" | awk '{print $8}' | sort | uniq | wc -l
```

---

## 💾 Backup و Recovery

### 1. Backup Script

```bash
# ایجاد backup.sh
cat > backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BOT_DIR="/path/to/telegram_bot"

# ایجاد پوشه backup
mkdir -p $BACKUP_DIR

# Backup database files
echo "Backing up databases..."
cp $BOT_DIR/user_data.db $BACKUP_DIR/user_data_$DATE.db
cp $BOT_DIR/content_data.db $BACKUP_DIR/content_data_$DATE.db

# Backup logs
echo "Backing up logs..."
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz $BOT_DIR/logs/

# Backup configuration
echo "Backing up config..."
cp $BOT_DIR/.env $BACKUP_DIR/env_$DATE.backup

# Remove old backups (keep last 30 days)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.backup" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x backup.sh
```

### 2. Recovery Process

```bash
# بازیابی از backup
restore_backup() {
    BACKUP_DATE=$1
    BOT_DIR="/path/to/telegram_bot"
    BACKUP_DIR="/path/to/backups"
    
    echo "Stopping bot..."
    sudo systemctl stop telegram-bot
    
    echo "Restoring databases..."
    cp $BACKUP_DIR/user_data_$BACKUP_DATE.db $BOT_DIR/user_data.db
    cp $BACKUP_DIR/content_data_$BACKUP_DATE.db $BOT_DIR/content_data.db
    
    echo "Restoring config..."
    cp $BACKUP_DIR/env_$BACKUP_DATE.backup $BOT_DIR/.env
    
    echo "Starting bot..."
    sudo systemctl start telegram-bot
    
    echo "Recovery completed"
}

# استفاده:
# restore_backup "20241201_020000"
```

### 3. Cloud Backup (اختیاری)

```bash
# AWS S3 backup
aws s3 sync /path/to/backups s3://your-backup-bucket/telegram-bot/

# rsync به server دیگر
rsync -avz /path/to/backups/ user@backup-server:/backups/telegram-bot/
```

---

## ⚡ بهینه‌سازی Performance

### 1. Database Optimization

```sql
-- اضافه کردن index های مفید
CREATE INDEX IF NOT EXISTS idx_progress_user_section 
ON progress(user_id, section, level);

CREATE INDEX IF NOT EXISTS idx_vocabulary_user 
ON vocabulary(user_id);

CREATE INDEX IF NOT EXISTS idx_user_grammar_user_level 
ON user_grammar(user_id, level);

-- Vacuum برای optimize کردن
VACUUM;
ANALYZE;
```

### 2. Python Optimization

```python
# در bot.py اضافه کنید:

# Connection pooling برای SQLite
import sqlite3
from threading import Lock

class DatabasePool:
    def __init__(self, db_path, pool_size=5):
        self.db_path = db_path
        self.pool = []
        self.lock = Lock()
        
        for _ in range(pool_size):
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self.pool.append(conn)
    
    def get_connection(self):
        with self.lock:
            if self.pool:
                return self.pool.pop()
            else:
                # Create new connection if pool is empty
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                conn.row_factory = sqlite3.Row
                return conn
    
    def return_connection(self, conn):
        with self.lock:
            self.pool.append(conn)

# استفاده
db_pool = DatabasePool("user_data.db")
```

### 3. Caching

```python
from functools import lru_cache
import time

# Cache برای محتوای ثابت
@lru_cache(maxsize=128)
def get_static_content(content_type, level):
    # محتوای ثابت که کمتر تغییر می‌کند
    return content_manager.get_content(content_type, level)

# Cache با TTL
class TTLCache:
    def __init__(self, ttl=300):
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key, value):
        self.cache[key] = (value, time.time())

# Global cache
user_cache = TTLCache(ttl=600)  # 10 minutes
```

### 4. Async Optimization

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Thread pool برای blocking operations
executor = ThreadPoolExecutor(max_workers=4)

async def async_db_operation(operation, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, operation, *args)

# استفاده
async def handle_user_progress(user_id):
    # اجرای database operation به صورت async
    progress = await async_db_operation(db.get_user_progress, user_id)
    return progress
```

---

## 🔐 امنیت

### 1. Environment Security

```bash
# تنظیم دسترسی فایل‌ها
chmod 600 .env
chmod 600 *.db
chmod 700 logs/

# اجرا با کاربر غیر privileged
sudo useradd -r -s /bin/false botuser
sudo chown -R botuser:botuser /path/to/telegram_bot
```

### 2. Network Security

```bash
# Firewall تنظیمات (UFW)
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 443  # اگر webhook استفاده می‌کنید

# یا برای Amazon Linux (iptables)
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -j DROP
```

### 3. Application Security

```python
# در bot.py اضافه کنید:

import re
from functools import wraps

def sanitize_input(text):
    """پاک‌سازی ورودی کاربر"""
    # حذف کاراکترهای خطرناک
    text = re.sub(r'[<>"\'\&]', '', text)
    # محدود کردن طول
    text = text[:500]
    return text.strip()

def rate_limit(max_calls=10, time_window=60):
    """محدودیت تعداد درخواست"""
    call_times = {}
    
    def decorator(func):
        @wraps(func)
        async def wrapper(update, context):
            user_id = update.effective_chat.id
            now = time.time()
            
            if user_id not in call_times:
                call_times[user_id] = []
            
            # پاک کردن درخواست‌های قدیمی
            call_times[user_id] = [t for t in call_times[user_id] if now - t < time_window]
            
            if len(call_times[user_id]) >= max_calls:
                await update.message.reply_text("لطفاً چند لحظه صبر کنید.")
                return
            
            call_times[user_id].append(now)
            return await func(update, context)
        return wrapper
    return decorator

# استفاده
@rate_limit(max_calls=5, time_window=60)
async def vocabulary_practice(update, context):
    # کد اصلی
    pass
```

### 4. API Security

```python
# محدودیت OpenAI API
import time

class APIRateLimiter:
    def __init__(self, max_calls_per_minute=20):
        self.max_calls = max_calls_per_minute
        self.calls = []
    
    async def wait_if_needed(self):
        now = time.time()
        # حذف calls قدیمی (بیشتر از 1 دقیقه)
        self.calls = [t for t in self.calls if now - t < 60]
        
        if len(self.calls) >= self.max_calls:
            wait_time = 60 - (now - self.calls[0])
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        self.calls.append(now)

# Global rate limiter
openai_limiter = APIRateLimiter(max_calls_per_minute=15)

async def safe_openai_call(prompt):
    await openai_limiter.wait_if_needed()
    return await call_openai_api(prompt)
```

---

## 🔧 عیب‌یابی

### مشکلات رایج و راه‌حل

#### 1. ربات پاسخ نمی‌دهد

```bash
# بررسی‌های اولیه
sudo systemctl status telegram-bot  # وضعیت service
tail -50 logs/bot.log               # آخرین logs

# بررسی اتصال شبکه
curl -I https://api.telegram.org
ping 8.8.8.8

# بررسی Token
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
token = os.getenv('TELEGRAM_BOT_TOKEN')
print('Token length:', len(token) if token else 'None')
print('Token starts with:', token[:10] if token else 'None')
"
```

#### 2. خطای OpenAI API

```bash
# بررسی API Key
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.openai.com/v1/models

# بررسی credit
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.openai.com/v1/usage

# تست ساده
python -c "
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

try:
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': 'Hello'}],
        max_tokens=10
    )
    print('Success:', response.choices[0].message.content)
except Exception as e:
    print('Error:', e)
"
```

#### 3. مشکل Database

```bash
# بررسی فایل‌های database
ls -la *.db
sqlite3 user_data.db "PRAGMA integrity_check;"

# بررسی ساختار
sqlite3 user_data.db ".schema"

# تعمیر database
sqlite3 user_data.db "VACUUM;"

# بازسازی از صفر (در صورت نیاز)
rm *.db
python bot.py  # دوباره ایجاد می‌شود
```

#### 4. مشکل Memory

```bash
# بررسی استفاده memory
free -h
ps aux | grep python

# Kill کردن processes اضافی
pkill -f "python bot.py"

# Restart service
sudo systemctl restart telegram-bot
```

### Debug Mode

```python
# در bot.py اضافه کنید:
import logging

# فعال‌سازی debug logging
logging.getLogger().setLevel(logging.DEBUG)

# اضافه کردن debug info
async def debug_info(update, context):
    user_id = update.effective_chat.id
    debug_text = f"""
🔧 Debug Information:
User ID: {user_id}
State: {user_states.get(user_id, 'Unknown')}
Level: {db.get_user_level(user_id)}
Time: {datetime.now()}
Python Version: {sys.version}
Bot Uptime: {time.time() - bot_start_time:.2f}s
"""
    await update.message.reply_text(debug_text)

# اضافه کردن به handlers
application.add_handler(CommandHandler("debug", debug_info))
```

### Health Check Endpoint

```python
# اضافه کردن health check
from telegram.ext import Application
import threading
import http.server
import socketserver

class HealthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'uptime': time.time() - bot_start_time
            }
            
            self.wfile.write(json.dumps(health_status).encode())
        else:
            self.send_response(404)
            self.end_headers()

def start_health_server():
    PORT = 8000
    handler = HealthHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        httpd.serve_forever()

# شروع health server در thread جداگانه
health_thread = threading.Thread(target=start_health_server, daemon=True)
health_thread.start()
```

---

## 📈 Scaling و Load Balancing

### Multi-Instance Setup

```bash
# اجرای چندین instance
# Instance 1
PORT=8001 python bot.py &

# Instance 2  
PORT=8002 python bot.py &

# Load balancer (nginx)
sudo nano /etc/nginx/sites-available/telegram-bot

# محتوا:
upstream telegram_bot {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://telegram_bot;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

**📝 نتیجه‌گیری:** این راهنمای استقرار تمام جنبه‌های deployment سیستم را پوشش می‌دهد. برای هر محیط، مراحل مناسب را دنبال کنید و برای مشکلات، بخش عیب‌یابی را مطالعه کنید.

---
*آخرین به‌روزرسانی: 2024*

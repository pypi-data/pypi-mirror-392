# 🚀 Logger Migration Guide - 5 Minutes

## Quick Setup

### Step 1: Save logger.py
Save the `logger.py` file in your project root.

### Step 2: Replace print() statements

**Find & Replace in your entire project:**

```python
# OLD → NEW

print(f"✅ {message}")          → success(message)
print(f"❌ {message}")          → error(message)
print(f"⚠️ {message}")          → warn(message)
print(f"ℹ️ {message}")          → info(message)
print(f"🐛 {message}")          → bug(message)
print(f"DEBUG: {message}")      → bug(message)
```

### Step 3: Add import at top of each file

```python
from logger import bug, info, warn, error, success
```

That's it! ✅

---

## Real Example: Update main.py

### BEFORE (your current code):
```python
@app.get("/auth/callback")
async def callback(request: Request):
    print(f"\n{'='*60}")
    print(f"🔄 OAuth Callback Received")
    print(f"   Query params: {dict(request.query_params)}")
    try:
        result = await auth.handle_callback(request)
        print(f"   ✅ Auth successful!")
        print(f"   User: {result.get('user', {}).get('email')}")
        print(f"{'='*60}\n")
        return create_auth_response(result, provider)
    except Exception as e:
        print(f"   ❌ Callback error: {e}")
        traceback.print_exc()
        print(f"{'='*60}\n")
        raise
```

### AFTER (with logger):
```python
from logger import info, error, success

@app.get("/auth/callback")
async def callback(request: Request):
    info("OAuth callback received", params=dict(request.query_params))
    
    try:
        result = await auth.handle_callback(request)
        success("Auth successful", user=result.get('user', {}).get('email'))
        return create_auth_response(result, provider)
    except Exception as e:
        error("Callback error", exc_info=True)
        raise
```

**Benefits:**
- ✅ Cleaner code (50% less lines)
- ✅ Automatic file/line detection
- ✅ Structured data (JSON in production)
- ✅ Color coding in development
- ✅ Exception tracing with `exc_info=True`

---

## Common Patterns

### Pattern 1: Simple Message
```python
# OLD
print("User logged in")

# NEW
info("User logged in")
```

### Pattern 2: Message with Data
```python
# OLD
print(f"User {user_id} logged in from {ip}")

# NEW
info("User logged in", user_id=user_id, ip=ip)
```

### Pattern 3: Error with Stack Trace
```python
# OLD
try:
    something()
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()

# NEW
try:
    something()
except Exception as e:
    error("Operation failed", exc_info=True)
```

### Pattern 4: Debug Info
```python
# OLD
print(f"DEBUG: Processing {len(items)} items")

# NEW
bug("Processing items", count=len(items))
```

### Pattern 5: Success Messages
```python
# OLD
print("✅ Payment processed successfully")

# NEW
success("Payment processed", order_id=order_id, amount=amount)
```

---

## Update Your Files

### main.py
```python
# Add at top
from logger import bug, info, warn, error, success, log_request, Timer

# Replace all print() statements
# Use @log_request decorator on endpoints
```

### Auth.py
```python
# Add at top
from logger import bug, info, warn, error, success

# Replace logger.info() with info()
# Replace logger.error() with error()
# Replace logger.warning() with warn()
```

### oauth.py
```python
# Add at top
from logger import bug, info, warn, error, success

# Same replacements as Auth.py
```

### google_auth.py
```python
# Add at top
from logger import bug, info, warn, error, success

# Replace logger.info() with info()
# etc.
```

---

## Advanced Features

### 1. Timing Operations
```python
from logger import Timer

timer = Timer()
# ... do something ...
timer.log("Database query completed")  # Logs with elapsed time
```

### 2. Log Code Blocks
```python
from logger import log_block

with log_block("Processing payment"):
    validate_payment()
    charge_card()
    send_confirmation()
# Automatically logs start/end with timing
```

### 3. Decorate Functions
```python
from logger import log_function_call

@log_function_call
def calculate_total(items):
    return sum(item.price for item in items)
# Automatically logs input/output
```

### 4. Decorate API Endpoints
```python
from logger import log_request

@app.get("/api/users")
@log_request("API")
async def get_users():
    return users
# Automatically logs request/response
```

---

## Configuration

### Development Mode (default)
```bash
# .env
ENVIRONMENT=development
```

**Output:**
- Colored console
- Emojis
- Shows DEBUG logs
- Pretty format

### Production Mode
```bash
# .env
ENVIRONMENT=production
LOG_FILE=/var/log/app.log  # Optional: log to file
```

**Output:**
- JSON format
- No DEBUG logs
- Machine readable
- Optimized performance

### Change Level Dynamically
```python
from logger import set_level

# In development, show everything
set_level('DEBUG')

# In staging, hide debug
set_level('INFO')

# In production, only warnings+
set_level('WARNING')
```

---

## Migration Checklist

- [ ] Save `logger.py` in project root
- [ ] Add `from logger import bug, info, warn, error, success` to each file
- [ ] Replace `print()` with logger functions
- [ ] Replace `logger.info()` with `info()`
- [ ] Replace `logger.error()` with `error()`
- [ ] Replace `logger.warning()` with `warn()`
- [ ] Add `exc_info=True` to error() calls where you want stack traces
- [ ] Test in development mode
- [ ] Test in production mode

---

## Comparison

### Without Logger (Current)
```python
print(f"\n{'='*60}")
print(f"📝 Profile Request")
print(f"   Cookies: {list(request.cookies.keys())}")
print(f"   Has token: {'access_token' in request.cookies}")

try:
    user = await get_user(request)
    print(f"   ✅ User: {user.get('email')}")
    print(f"{'='*60}\n")
    return user
except Exception as e:
    print(f"   ❌ Error: {e}")
    print(traceback.format_exc())
    print(f"{'='*60}\n")
    raise
```

**Issues:**
- ❌ Manual formatting
- ❌ No structure
- ❌ Can't filter by level
- ❌ No machine-readable format
- ❌ Hard to search logs
- ❌ Verbose code

### With Logger (New)
```python
info("Profile request", 
     cookies=list(request.cookies.keys()),
     has_token='access_token' in request.cookies)

try:
    user = await get_user(request)
    success("User retrieved", email=user.get('email'))
    return user
except Exception as e:
    error("Profile fetch failed", exc_info=True)
    raise
```

**Benefits:**
- ✅ Clean code
- ✅ Structured data
- ✅ Filterable logs
- ✅ JSON output in prod
- ✅ Searchable logs
- ✅ Concise

---

## Log Levels Guide

| Function | Level | Use For | Production |
|----------|-------|---------|------------|
| `bug()` | DEBUG | Development debugging | Hidden |
| `info()` | INFO | Normal operations | Shown |
| `success()` | SUCCESS | Positive outcomes | Shown |
| `warn()` | WARNING | Potential issues | Shown |
| `error()` | ERROR | Errors | Shown |
| `critical()` | CRITICAL | System failures | Shown |

---

## Pro Tips

### 1. Use bug() for Development
```python
bug("User data", user=user.__dict__)  # Only shows in dev
```

### 2. Use Structured Data
```python
# BAD
info(f"User {user_id} from {country} bought {item}")

# GOOD
info("Purchase", user_id=user_id, country=country, item=item)
```

### 3. Add Context
```python
info("API call", 
     endpoint="/api/users",
     method="GET",
     user_id=current_user.id,
     duration_ms=123)
```

### 4. Use exc_info for Errors
```python
try:
    risky_operation()
except Exception:
    error("Operation failed", exc_info=True)  # Includes full stack trace
```

### 5. Time Long Operations
```python
from logger import Timer

timer = Timer()
result = long_database_query()
timer.log("Query completed", rows=len(result))
```

---

## Testing

### Run your app:
```bash
python main.py
```

### You'll see (development mode):
```
12:34:56.789 │ ℹ️  │ INFO     │ main.py:42           │ Server starting │ {"port": 9000}
12:34:56.890 │ ✅ │ SUCCESS  │ auth.py:156          │ Auth initialized
12:34:57.123 │ ℹ️  │ INFO     │ main.py:50           │ Server ready
```

### In production (JSON):
```json
{"timestamp":"2025-01-15T12:34:56.789","level":"INFO","message":"Server starting","file":"main.py","line":42,"data":{"port":9000}}
{"timestamp":"2025-01-15T12:34:56.890","level":"SUCCESS","message":"Auth initialized","file":"auth.py","line":156}
```

---

## Summary

**Before:**
- Using `print()`
- 500+ lines of formatting code
- Unstructured logs
- Hard to debug in production

**After:**
- Using `bug()`, `info()`, `error()`, etc.
- Clean, readable code
- Structured JSON logs
- Easy debugging everywhere

**Effort:** 10 minutes  
**Impact:** Huge! 🚀

---

## Need Help?

**Q: Will this break my existing code?**  
A: No! You can gradually migrate. Old `print()` still works.

**Q: What about existing logger.info()?**  
A: Just replace with `info()` - same functionality, better output.

**Q: Performance impact?**  
A: Minimal. Actually faster in production (optimized JSON output).

**Q: Can I use both print() and logger?**  
A: Yes, but better to stick with logger for consistency.

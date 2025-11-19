# Release Notes - v0.3.0

**Release Date**: November 17, 2025
**Type**: Feature Release
**Focus**: High-Priority Endpoint Coverage

---

## 🎯 Summary

Version 0.3.0 adds **4 critical HIGH PRIORITY endpoints** identified through comprehensive audit of the Marqeta DiVA API documentation. This release significantly improves endpoint coverage from **50% to 67%**, focusing on the most commonly needed functionality:

1. **Transaction Token Mapping** - Critical for reconciliation workflows
2. **Card Counts** - Essential for program monitoring
3. **User Counts** - Essential for growth tracking
4. **Network Detail** - Important for network analytics

---

## ✨ New Features

### 1. Transaction Token Mapping (`get_transaction_token`) ⭐ EMPHASIS

**Endpoint**: `/views/transactiontoken`

**Purpose**: Map Core API transaction tokens to DiVA report transaction tokens

**Why It Matters**:
- **CRITICAL** for reconciliation between webhook data and DiVA reports
- Links real-time transaction events to aggregated reporting data
- Essential for financial reconciliation workflows
- Bridges the gap between operational and analytical systems

**Use Cases**:
- Reconcile webhook transaction events with DiVA reports
- Match Core API transaction data to report data
- Build comprehensive transaction tracking systems
- Audit and compliance workflows

**Example Usage**:
```json
{
  "tool": "get_transaction_token",
  "filters": {
    "core_api_transaction_token": "xyz123"
  },
  "count": 100
}
```

**Returns**: Mapping between Core API tokens and DiVA tokens

---

### 2. Card Counts (`get_card_counts`)

**Endpoint**: `/views/cardcounts/{time_agg}` (day, week, month)

**Purpose**: Track card program metrics over time

**Why It Matters**:
- Monitor card program health and growth
- Track cards in circulation, active, suspended states
- Essential KPIs for program managers
- Identify trends and anomalies

**Use Cases**:
- Daily/weekly/monthly card program reports
- Monitor card activation rates
- Track suspended card volumes
- Program growth analytics

**Aggregation Levels**: day, week, month (no detail level)

**Example Usage**:
```json
{
  "tool": "get_card_counts",
  "aggregation": "day",
  "count": 30
}
```

**Returns**: Card count metrics by state, type, and time period

---

### 3. User Counts (`get_user_counts`)

**Endpoint**: `/views/usercounts/{time_agg}` (day, week, month)

**Purpose**: Track user base growth and engagement

**Why It Matters**:
- Monitor program user growth
- Track user account states
- Identify engagement patterns
- Forecast capacity needs

**Use Cases**:
- User growth dashboards
- Engagement analytics
- Program adoption tracking
- Capacity planning

**Aggregation Levels**: day, week, month (no detail level)

**Example Usage**:
```json
{
  "tool": "get_user_counts",
  "aggregation": "week",
  "filters": {
    "user_type": "BUSINESS"
  }
}
```

**Returns**: User count metrics by type, status, and time period

---

### 4. Activity Balances Network Detail (`get_activity_balances_network_detail`)

**Endpoint**: `/views/activitybalances/day/networkdetail`

**Purpose**: Break out transaction data by card network

**Why It Matters**:
- Analyze network-specific transaction volumes
- Understand Visa vs Mastercard vs other network usage
- Optimize network relationships and costs
- Detailed network performance analytics

**Use Cases**:
- Network volume analysis
- Network cost optimization
- Routing decision support
- Network performance reporting

**Aggregation**: Day only (fixed)

**Expandable Fields**:
- `pin_purchases_net` - Break out PIN purchases by network (Visa, Mastercard, Maestro, Cirrus, etc.)
- `sig_purchases_net` - Break out signature purchases by network

**Example Usage**:
```json
{
  "tool": "get_activity_balances_network_detail",
  "expand": "pin_purchases_net,sig_purchases_net",
  "count": 10
}
```

**Returns**: Activity balance data with network-specific breakdowns

---

## 📊 Coverage Improvement

### Before v0.3.0:
- **12 endpoints** implemented
- **50% coverage** of DiVA API

### After v0.3.0:
- **16 endpoints** implemented
- **67% coverage** of DiVA API
- **All HIGH PRIORITY endpoints** covered

### Remaining Gaps:
- 8 MEDIUM/LOW priority endpoints (specialized use cases)
- See ENDPOINT_AUDIT.md for complete analysis

---

## 🧪 Testing

New test script provided: `test_new_endpoints.py`

Run tests:
```bash
python test_new_endpoints.py
```

Tests verify:
- Endpoint connectivity
- Response format
- Data retrieval
- Error handling

---

## 📚 Documentation Updates

### New Files:
- **ENDPOINT_AUDIT.md** - Comprehensive audit of all DiVA endpoints
- **RELEASE_NOTES_v0.3.0.md** - This file
- **test_new_endpoints.py** - Test script for new endpoints

### Updated Files:
- **server.py** - Added 4 new tools and handlers
- **pyproject.toml** - Version bump to 0.3.0
- **README.md** - (Pending update with new endpoints)

---

## 🔧 Technical Implementation

### Code Structure:
```python
# New tools added to BASE_TOOLS:
- get_transaction_token (Reconciliation Tools section)
- get_card_counts (Count/Monitoring Tools section)
- get_user_counts (Count/Monitoring Tools section)
- get_activity_balances_network_detail (Network Analytics Tools section)
```

### View Names:
```python
"transactiontoken"           # No aggregation
"cardcounts"                 # day/week/month aggregation
"usercounts"                 # day/week/month aggregation
"activitybalances/day/networkdetail"  # Fixed day aggregation
```

### All Endpoints Use Standard Pattern:
```python
result = client.get_view(view_name, aggregation, **arguments)
```

---

## 🚀 Upgrade Instructions

### For Existing Users:

1. **Pull latest changes** (if using git):
   ```bash
   git pull origin main
   ```

2. **Update package** (if using PyPI):
   ```bash
   pip install --upgrade marqeta-diva-mcp
   ```

3. **Verify version**:
   ```python
   from src.marqeta_diva_mcp.server import SERVER_VERSION
   print(SERVER_VERSION)  # Should show "0.3.0"
   ```

4. **Restart MCP server** (if running):
   - Claude Desktop: Restart the application
   - Claude Code: Restart the server process

5. **Test new endpoints**:
   ```bash
   python test_new_endpoints.py
   ```

---

## ⚠️ Breaking Changes

**NONE** - This is a backward-compatible feature release.

All existing endpoints continue to work exactly as before. The new endpoints are purely additive.

---

## 🐛 Bug Fixes

No bug fixes in this release (feature-only release).

---

## 📝 Notes

### Endpoint Availability:
Not all programs have access to all endpoints. If you receive authorization errors:
1. Check with your Marqeta representative
2. Verify your credentials have access to these views
3. Some views may be limited to specific program types

### Data Availability:
Some views may return empty results if:
- Your program is newly created
- You haven't generated relevant activity yet
- Data is still being synchronized (3x daily sync)

### Performance:
- All endpoints respect the 10,000 record API limit
- Use filters and date ranges for large datasets
- Rate limiting applies: 300 requests per 5 minutes

---

## 🔮 What's Next?

### Planned for v0.4.0 (Future):
Potential MEDIUM PRIORITY endpoints:
- Direct Deposit (`directdeposit/detail`)
- ACH Origination (`achorigination/detail`)
- Platform Response (`platformresponse/month`)
- RTD Transaction Count by Rules (`cptrxn/rule/detail`)

Vote for features or request new endpoints in [GitHub Issues](https://github.com/zvika-finally/marqeta-diva-mcp/issues).

---

## 💬 Feedback

Questions or issues with the new endpoints? Please:
1. Check ENDPOINT_AUDIT.md for detailed information
2. Run test_new_endpoints.py to verify your setup
3. Open an issue on GitHub if you encounter problems

---

## 🙏 Acknowledgments

This release was driven by comprehensive documentation audit and user feedback prioritizing reconciliation and monitoring capabilities.

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👤 Author

**Zvika Badalov** - zvika.badalov@finally.com

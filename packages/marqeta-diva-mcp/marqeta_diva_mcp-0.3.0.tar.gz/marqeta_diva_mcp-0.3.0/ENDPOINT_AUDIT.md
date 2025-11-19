# DiVA API Endpoint Coverage Audit

**Date**: November 17, 2025
**Auditor**: Claude Code
**Method**: Comprehensive scrape of official Marqeta DiVA API documentation

## Executive Summary

After scraping all 28 documentation pages from https://www.marqeta.com/docs/diva-api/, I found that our MCP server implements **12 out of 24 endpoints** (~50% coverage).

**Missing: 12 endpoints** that could provide valuable data for users.

---

## ✅ Implemented Endpoints (12)

### Transaction Tools
1. **get_authorizations** → `/views/authorizations/{time_agg}`
2. **get_settlements** → `/views/settlements/{time_agg}`
3. **get_clearings** → `/views/clearing/{time_agg}`
4. **get_declines** → `/views/declines/{time_agg}`
5. **get_loads** → `/views/loads/{time_agg}`

### Financial Tools
6. **get_program_balances** → `/views/programbalances/day`
7. **get_program_balances_settlement** → `/views/programbalancessettlement/day`
8. **get_activity_balances** → `/views/activitybalances/day`

### Card & User Tools
9. **get_cards** → `/views/cards/detail`
10. **get_users** → `/views/users/detail`

### Chargeback Tools
11. **get_chargebacks_status** → `/views/chargebacks/status`
12. **get_chargebacks_detail** → `/views/chargebacks/detail`

---

## ❌ Missing Endpoints (12)

### HIGH PRIORITY (Common Use Cases)

#### 1. Card Counts
- **Endpoint**: `/views/cardcounts/{time_agg}` (day, week, month)
- **Purpose**: Card count metrics - cards in circulation, active, suspended
- **Use Case**: Track card program growth and health metrics
- **Data**: Card counts by state, type, and time period
- **Priority**: HIGH - Essential for program monitoring

#### 2. User Counts
- **Endpoint**: `/views/usercounts/{time_agg}` (day, week, month)
- **Purpose**: User count metrics - users with accounts, suspended accounts
- **Use Case**: Track user base growth and engagement
- **Data**: User counts by type, status, and time period
- **Priority**: HIGH - Essential for program monitoring

#### 3. Activity Balances Network Detail
- **Endpoint**: `/views/activitybalances/day/networkdetail`
- **Purpose**: Activity balances broken out by card network (Visa, Mastercard, etc.)
- **Use Case**: Analyze transaction volumes by network
- **Data**: PIN/signature purchases by network, expandable fields
- **Priority**: HIGH - Important for network analysis
- **Note**: We have `activitybalances` but not the network detail variant

#### 4. Core API Transaction Token
- **Endpoint**: `/views/transactiontoken`
- **Purpose**: Map Core API transaction tokens to DiVA report transaction tokens
- **Use Case**: Reconciliation between Core API and DiVA data
- **Data**: Token mappings for cross-system reconciliation
- **Priority**: HIGH - Critical for reconciliation workflows

### MEDIUM PRIORITY (Specialized Features)

#### 5. Direct Deposit
- **Endpoint**: `/views/directdeposit/detail`
- **Purpose**: Direct deposit transaction data
- **Use Case**: Track direct deposit usage and volumes
- **Data**: Direct deposit amounts, settlement dates, user tokens
- **Priority**: MEDIUM - Only for programs using Direct Deposit product

#### 6. ACH Origination
- **Endpoint**: `/views/achorigination/detail`
- **Purpose**: ACH origination transfers for Program & User Funding
- **Use Case**: Track ACH transfer details
- **Data**: Transfer amounts, currencies, statuses
- **Priority**: MEDIUM - Only for programs using ACH

#### 7. Platform Response
- **Endpoint**: `/views/platformresponse/month` (month aggregation only)
- **Purpose**: JIT gateway transactions, average durations
- **Use Case**: Monitor platform performance metrics
- **Data**: Transaction counts, response times, gateway durations
- **Priority**: MEDIUM - Performance monitoring

#### 8. RTD Transaction Count by Rules
- **Endpoint**: `/views/cptrxn/rule/detail`
- **Purpose**: Real-Time Decisioning - transaction counts per triggered rule
- **Use Case**: Fraud/risk rule analysis
- **Data**: Rule names, triggered transactions, amounts
- **Priority**: MEDIUM - For programs using Real-Time Decisioning

### LOW PRIORITY (Credit Product Only)

#### 9. Credit Journal Entries
- **Endpoint**: `/views/credit/journalentries/detail`
- **Purpose**: Journal entries for credit accounts
- **Use Case**: Credit account balance tracking
- **Data**: Journal entry details, amounts, timestamps
- **Priority**: LOW - Only for credit card programs

#### 10. Credit Payments
- **Endpoint**: `/views/credit/payments/detail`
- **Purpose**: Payment details for credit accounts
- **Use Case**: Track credit card payments
- **Data**: Payment amounts, dates, methods
- **Priority**: LOW - Only for credit card programs

### LIMITED AVAILABILITY

#### 11. ACH Gateway
- **Endpoint**: `/views/achgateways`
- **Purpose**: ACH gateway transaction data
- **Use Case**: ACH transaction monitoring
- **Data**: ACH gateway messages and responses
- **Priority**: LOW - Limited availability, requires special configuration
- **Note**: Documentation says "limited in availability"

### DEPRECATED

#### 12. Credit Ledger Entries
- **Endpoint**: `/views/credit/ledgerentries/detail`
- **Purpose**: Ledger entries for credit accounts (DEPRECATED)
- **Use Case**: Being replaced by journal entries
- **Data**: Legacy ledger entry data
- **Priority**: SKIP - Documentation warns this is deprecated
- **Note**: Will be replaced by journal entries, contact Marqeta rep

---

## Implementation Recommendations

### Immediate Action (Version 0.3.0)

Add the **HIGH PRIORITY** endpoints:

1. **get_card_counts** - Essential for monitoring
2. **get_user_counts** - Essential for monitoring
3. **get_activity_balances_network_detail** - Important analytics
4. **get_transaction_token** - Critical for reconciliation

**Estimated effort**: 4-6 hours
**Impact**: HIGH - These are commonly used endpoints

### Short Term (Version 0.4.0)

Add **MEDIUM PRIORITY** endpoints that apply broadly:

5. **get_direct_deposit** - If Direct Deposit is commonly used
6. **get_ach_origination** - If ACH is commonly used
7. **get_platform_response** - Performance monitoring

**Estimated effort**: 3-4 hours
**Impact**: MEDIUM - Specialized but valuable

### Future Consideration

- **Credit-specific endpoints** - Add if demand exists from credit card programs
- **RTD endpoints** - Add if Real-Time Decisioning users request it
- **ACH Gateway** - Skip unless users explicitly need it (limited availability)
- **Credit Ledger** - SKIP (deprecated)

---

## Technical Implementation Notes

### Pattern Observed

All endpoints follow the same pattern:
```python
Tool(
    name="get_<view_name>",
    description="...",
    inputSchema={
        "type": "object",
        "properties": {
            "aggregation": {...},  # If time-aggregated
            "fields": {...},
            "filters": {...},
            "sort_by": {...},
            "count": {...},
            "expand": {...},  # If expandable
            "program": {...}
        }
    }
)
```

### Client Method

All use the same `client.get_view()` method:
```python
result = client.get_view(view_name, aggregation, **arguments)
```

### View Names

Marqeta uses these view name conventions:
- **Transaction views**: `authorizations`, `settlements`, `clearing`, `declines`, `loads`
- **Count views**: `cardcounts`, `usercounts`
- **Balance views**: `programbalances`, `activitybalances`
- **Credit views**: `credit/journalentries`, `credit/payments`, `credit/ledgerentries`
- **ACH views**: `achgateways`, `achorigination`
- **Special**: `directdeposit`, `platformresponse`, `transactiontoken`, `cptrxn/rule`

---

## Testing Recommendations

Before adding new endpoints:

1. **Verify access**: Not all programs have access to all endpoints
2. **Test aggregation levels**: Some endpoints only support certain aggregations
3. **Check schemas**: Use `get_view_schema()` to understand available fields
4. **Document limitations**: Note which features require special configuration

---

## Questions for User

1. **Which endpoints are most critical for your use cases?**
   - Card/user counts for monitoring?
   - Transaction token mapping for reconciliation?
   - Network detail for analytics?

2. **Do you use these specialized products?**
   - Direct Deposit
   - ACH Origination
   - Credit card programs
   - Real-Time Decisioning

3. **Should I implement all missing endpoints or just high-priority ones?**

---

## Conclusion

Our current implementation covers the **core transaction and balance endpoints** well, but misses important **monitoring** (card/user counts), **reconciliation** (transaction token), and **analytics** (network detail) endpoints.

**Recommendation**: Add the 4 HIGH PRIORITY endpoints in version 0.3.0 to significantly improve coverage and user value.

# Function Calling Implementation - Testing Guide

## Overview

The cite-agent has been redesigned to use **proper function calling** instead of keyword matching. This fixes:
- ✅ Archive API spam on conversational queries
- ✅ Hallucinated file listings (forces tool execution)
- ✅ Brittle keyword matching edge cases
- ✅ Sets foundation for reliable multi-tool workflows

## What Changed

### Architecture Shift

**Before (Keyword Matching - BROKEN)**
```python
if "paper" in query or "research" in query:
    apis_to_use.append("archive")  # Spam Archive API
if "code" in query:  # "did you hardcode this?"
    apis_to_use.append("archive")  # WHY?!
```

**After (Function Calling - PROPER)**
```python
response = client.chat.completions.create(
    model="llama-3.3-70b",
    messages=[{"role": "user", "content": query}],
    tools=TOOLS,  # LLM chooses
    tool_choice="auto"
)
# LLM intelligently chooses appropriate tools
```

### Files Added

1. **cite_agent/function_tools.py** - 8 tool definitions with OpenAI-compatible schemas
2. **cite_agent/function_calling.py** - FunctionCallingAgent class for orchestrating LLM tool calls
3. **cite_agent/tool_executor.py** - ToolExecutor class bridges function calling → existing agent capabilities
4. **cite_agent/function_calling_integration.py** - Integration documentation

### Files Modified

- **cite_agent/enhanced_ai_agent.py** - Added `process_request_with_function_calling()` and routing logic

## Prerequisites for Testing

### 1. Temp API Key (Recommended - 10x faster)

Login to get a temp Cerebras API key (valid for 14 days):

```bash
cite-agent login
```

This will:
- Issue a 14-day Cerebras API key from backend
- Store it in `~/.nocturnal_archive/session.json`
- Enable local function calling mode (10x faster than backend)

### 2. OR Local API Keys (Alternative)

Set environment variable:

```bash
export CEREBRAS_API_KEY="your-key-here"
# OR
export GROQ_API_KEY="your-key-here"
# OR
export OPENAI_API_KEY="your-key-here"
```

### 3. Verify Setup

```bash
# Check temp key status
bash scripts/check_temp_key.sh

# Should show:
# ✅ KEY VALID (XXX hours remaining)
```

## Testing Workflow

### Step 1: Enable Debug Mode

```bash
export NOCTURNAL_DEBUG=1
```

This will show:
- `🔍 [Function Calling]` logs for workflow tracking
- Tool execution logs (`📚 Archive API`, `💰 FinSight`, `🌐 Web Search`)
- Token usage and response generation

### Step 2: Test Problematic Queries (Previously Broken)

#### Test 1: "test" → Should NOT spam Archive API

**What it should do:**
- Detect simple chat query
- Return instant response (no LLM call, no API calls)
- 0 tokens used

```bash
echo "test" | cite-agent chat
```

**Expected output:**
```
🔍 [Function Calling] Simple chat query detected, quick response
I'm ready to help. What would you like to work on?

Tokens used: 0
Tools used: quick_reply
```

**Old behavior (BROKEN):**
- Called Archive API 10 times
- Wasted tokens on LLM call
- Took 5+ seconds

---

#### Test 2: "did you hardcode this?" → Should use 'chat' tool only

**What it should do:**
- LLM chooses `chat` tool (conversational response)
- NO Archive API calls
- ~50-100 tokens

```bash
echo "did you hardcode this?" | cite-agent chat
```

**Expected output:**
```
🔍 [Function Calling] Processing query: did you hardcode this?...
🔍 [Function Calling] No tool calls, direct response
[Conversational response about the system]

Tokens used: ~80
Tools used: chat
```

**Old behavior (BROKEN):**
- "code" keyword triggered Archive API
- 10 Archive API searches for papers
- "did you hardcode" is meta question, not research

---

#### Test 3: "what folders can you see?" → Should execute 'list_directory'

**What it should do:**
- LLM chooses `list_directory` tool
- Executes actual `ls` command
- Returns REAL folder listing

```bash
echo "what folders can you see?" | cite-agent chat
```

**Expected output:**
```
🔍 [Function Calling] Processing query: what folders can you see?...
🔍 [Function Calling] Executing 1 tool(s)
📁 [List Directory] Path: ., show_hidden: false
[Real folder listing]

Tools used: list_directory
```

**Old behavior (BROKEN):**
- LLM hallucinated folders: data/, scripts/, results/, notes/
- Never executed actual `ls` command

---

### Step 3: Test Legitimate Tool Usage

#### Test 4: "find papers on transformers" → Should use 'search_papers'

```bash
echo "find papers on transformers" | cite-agent chat
```

**Expected output:**
```
🔍 [Function Calling] Processing query: find papers on transformers...
🔍 [Function Calling] Executing 1 tool(s)
📚 [Archive API] Searching: transformers (limit=5, sources=['semantic_scholar', 'openalex'])
📚 [Archive API] Found X papers
🔍 [Function Calling] Getting final response with tool results
[Synthesized response with paper citations]

Tools used: search_papers
```

---

#### Test 5: "Apple revenue" → Should use 'get_financial_data'

```bash
echo "Apple revenue" | cite-agent chat
```

**Expected output:**
```
🔍 [Function Calling] Processing query: Apple revenue...
🔍 [Function Calling] Executing 1 tool(s)
💰 [FinSight API] Getting data for AAPL: ['revenue', 'profit', 'market_cap']
💰 [FinSight API] Retrieved X metrics
🔍 [Function Calling] Getting final response with tool results
[Synthesized response with financial data]

Tools used: get_financial_data
```

---

#### Test 6: "latest AI news" → Should use 'web_search'

```bash
echo "latest AI news" | cite-agent chat
```

**Expected output:**
```
🔍 [Function Calling] Processing query: latest AI news...
🔍 [Function Calling] Executing 1 tool(s)
🌐 [Web Search] Searching: latest AI news (num_results=5)
🌐 [Web Search] Found X results
🔍 [Function Calling] Getting final response with tool results
[Synthesized response with web results]

Tools used: web_search
```

---

### Step 4: Test Multi-Tool Workflows

#### Test 7: "compare Apple and Microsoft revenue"

**What it should do:**
- LLM chooses `get_financial_data` tool TWICE (once for each company)
- Executes both in sequence
- Synthesizes comparison

```bash
echo "compare Apple and Microsoft revenue" | cite-agent chat
```

**Expected output:**
```
🔍 [Function Calling] Processing query: compare Apple and Microsoft revenue...
🔍 [Function Calling] Executing 2 tool(s)
💰 [FinSight API] Getting data for AAPL: ['revenue', 'profit', 'market_cap']
💰 [FinSight API] Getting data for MSFT: ['revenue', 'profit', 'market_cap']
🔍 [Function Calling] Getting final response with tool results
[Comparison with both companies' data]

Tools used: get_financial_data, get_financial_data
```

---

## Debugging Issues

### Issue: "Backend is busy"

**Cause:** No temp key and backend is unavailable

**Solution:**
```bash
# Get temp key
cite-agent login

# OR set local API key
export CEREBRAS_API_KEY="your-key"
```

---

### Issue: Still using backend mode

**Check routing logic:**
```bash
# Should show client initialization
NOCTURNAL_DEBUG=1 cite-agent chat
# Look for: "🔍 [Function Calling] Processing query..."
```

**If you see old logs instead:**
- Check `self.client is not None` in enhanced_ai_agent.py line 3744
- Verify temp key: `bash scripts/check_temp_key.sh`

---

### Issue: AttributeError on tool execution

**Example:** `AttributeError: 'EnhancedNocturnalAgent' object has no attribute 'archive_api'`

**Solution:** This was fixed in commit b66f59e. Make sure you're on the latest branch:
```bash
git pull origin claude/first-things-first-01BWTYHVH8gENVukcBPrm17K
```

---

## Success Criteria

All tests should:
1. ✅ Show `🔍 [Function Calling]` logs (proves function calling mode)
2. ✅ Use appropriate tools (no Archive spam on "test")
3. ✅ Execute tools correctly (no hallucinated folders)
4. ✅ Synthesize coherent responses
5. ✅ Report correct token usage

---

## Next Steps After Testing

1. **If tests pass:** Function calling implementation is working! 🎉
2. **Backend integration:** cite-agent-api needs similar function calling implementation
3. **Remove old code:** Delete keyword matching logic from enhanced_ai_agent.py
4. **Monitor production:** Watch for edge cases and tool selection quality

---

## Related Documentation

- [Temp API Key System](./TEMP_API_KEY_SYSTEM.md) - How temp keys work
- [Function Calling Integration](../cite_agent/function_calling_integration.py) - Code integration details
- [Tool Definitions](../cite_agent/function_tools.py) - All 8 available tools

---

## Commit History

- `995ec1a` - ✨ Feature: Replace keyword matching with proper function calling
- `b66f59e` - 🐛 Fix: Correct API method calls in tool_executor

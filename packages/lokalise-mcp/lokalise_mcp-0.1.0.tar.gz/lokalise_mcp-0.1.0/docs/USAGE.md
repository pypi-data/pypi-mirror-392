# Lokalise MCP - Usage Guide

Learn how to use the Lokalise MCP server to extract and sync translation keys.

## Quick Start

The Lokalise MCP provides three main tools:

1. **get_lokalise_project_info** - Check your project configuration
2. **preview_new_keys** - See what keys would be extracted (dry run)
3. **extract_and_sync_translations** - Extract and create keys in Lokalise

## Tool 1: Check Project Information

Before starting, verify your Lokalise project connection:

```
Use the get_lokalise_project_info tool
```

**Example Response:**
```json
{
  "project_id": "123456abc.def",
  "project_name": "My Application",
  "base_language": "en",
  "languages": [
    {"code": "en", "name": "English", "is_base": true},
    {"code": "no", "name": "Norwegian", "is_base": false},
    {"code": "th", "name": "Thai", "is_base": false},
    {"code": "sv", "name": "Swedish", "is_base": false}
  ],
  "total_languages": 4
}
```

This confirms:
- ✅ API connection works
- ✅ Project ID is correct
- ✅ Languages are configured (translations will be created for all of these)

## Tool 2: Preview New Keys (Dry Run)

Before creating keys, preview what would be extracted from your current branch:

```
Use preview_new_keys with base_branch="main"
```

**Example Response:**
```json
{
  "total_keys": 12,
  "namespaces": {
    "products": [
      {
        "key": "products.landing.title",
        "default": "Product Landing",
        "file": "src/pages/ProductLanding.tsx",
        "line": 23,
        "has_default": true
      },
      {
        "key": "products.list.empty",
        "default": "No products found",
        "file": "src/components/ProductList.tsx",
        "line": 45,
        "has_default": true
      }
    ],
    "actions": [
      {
        "key": "actions.addToCart",
        "default": "Add to Cart",
        "file": "src/components/ProductCard.tsx",
        "line": 67,
        "has_default": true
      }
    ]
  },
  "missing_defaults": [
    {
      "key": "products.filters.category",
      "file": "src/pages/ProductLanding.tsx",
      "line": 52,
      "context": "<Select label=???>{t('products.filters.category')}</Select>"
    }
  ]
}
```

This shows:
- 📊 Total keys found
- 📁 Keys grouped by namespace
- ⚠️ Keys missing default values (you'll need to provide these)
- 📍 Exact file location for each key

## Tool 3: Extract and Sync Translations

Once you've reviewed the preview, run the full sync:

```
Use extract_and_sync_translations with:
  - base_branch="main"
  - batch_size=3
  - auto_approve=false (to review each batch)
```

### Workflow Steps

The tool will:

1. **Extract keys** from files changed in your branch
2. **Run safety checks** on source text
3. **Fetch languages** from Lokalise
4. **Generate AI translations** for all target languages
5. **Verify translations** don't introduce harmful content
6. **Create keys in Lokalise** in batches of 3

**Example Response:**
```json
{
  "status": "completed",
  "total_keys_found": 12,
  "created": 11,
  "skipped": 1,
  "failed": 0,
  "flagged_keys": [],
  "errors": [],
  "languages": ["en", "no", "th", "sv"]
}
```

## Understanding the Translation Pattern

The MCP looks for these patterns in your code:

### Pattern 1: With Default Value (Recommended)

```typescript
t('employee.assignmentDetails.general.deleteAssignment', { _: 'Delete Assignment' })
```

- ✅ Extracts key: `employee.assignmentDetails.general.deleteAssignment`
- ✅ Uses `Delete Assignment` as English text
- ✅ AI translates to other languages

### Pattern 2: Without Default

```typescript
t('actions.save')
```

- ✅ Extracts key: `actions.save`
- ⚠️ No default value - you'll need to provide one

### Pattern 3: With Parameters

```typescript
t('actions.selectedEmployees', { count: 5, _: '%{count} employees selected' })
```

- ✅ Extracts key and detects `{count}` parameter
- ✅ Preserves parameter in translations

### Pattern 4: useTranslate Hook

```typescript
const translate = useTranslate();
translate('actions.cancel');
```

- ✅ Also detected and extracted

## Safety Checks

The MCP includes content safety guards to prevent harmful translations:

### What Gets Flagged

- Profanity or abusive language
- Hate speech
- Discriminatory content
- Violent language (unless contextually appropriate)

### Example: Safe Technical Term

```typescript
// This is OK - technical context
t('process.kill', { _: 'Kill process' })
```

**Safety Check Result:** ✅ APPROVED (technical term in system context)

### Example: Flagged Content

```typescript
// This would be flagged
t('error.message', { _: 'You are stupid' })
```

**Safety Check Result:** ⚠️ UNSAFE - Abusive language detected

### Disabling Safety Checks

If you're confident in your content:

```
Use extract_and_sync_translations with:
  - skip_safety_check=true
```

## Common Workflows

### Workflow 1: Feature Branch Translation

After implementing a new feature:

```bash
# 1. Create feature branch
git checkout -b feature/product-landing

# 2. Write code with translation keys
# (use pattern: t('key', { _: 'Default Text' }))

# 3. Preview what will be extracted
Use preview_new_keys

# 4. Extract and sync
Use extract_and_sync_translations

# 5. Create PR to sync Lokalise → local JSON files
```

### Workflow 2: Bulk Translation Update

After making many changes:

```bash
# 1. Preview all changes
Use preview_new_keys with base_branch="main"

# 2. Review the output carefully

# 3. Sync in batches
Use extract_and_sync_translations with batch_size=5

# 4. Check Lokalise dashboard to verify
```

## Configuration Options

### Per-Project Configuration

Edit `.lokalise-mcp.json`:

```json
{
  "baseBranch": "develop",        // Compare against develop instead of main
  "batchSize": 5,                 // Create 5 keys per batch
  "filePatterns": ["**/*.tsx"],   // Only scan .tsx files
  "safety": {
    "enabled": false              // Disable safety checks
  }
}
```

### Per-Command Options

Override config when using tools:

```
Use extract_and_sync_translations with:
  - base_branch="develop"    // Compare against different branch
  - batch_size=10            // Larger batches
  - auto_approve=true        // Skip approval prompts
  - skip_safety_check=true   // Disable safety checks
```

## Next Steps

After keys are created in Lokalise:

1. Review translations in Lokalise dashboard
2. Make manual adjustments if needed
3. Create PR to sync Lokalise → local JSON files (your existing workflow)
4. Merge and deploy

## Troubleshooting

### "No translation keys found in changed files"

- Make sure you're on a feature branch (not main)
- Check that files match the configured patterns (*.tsx, *.ts, etc.)
- Verify translation functions are named `t()` or `translate()`

### "Key already exists - skipped"

The key is already in Lokalise. This is normal and prevents duplicates.

### Safety check flagged my text

Review the context - if it's a legitimate use (like technical error messages), you can:
1. Adjust the wording to be more professional
2. Use `skip_safety_check=true` if you're confident

## Best Practices

1. **Always use default values**: `t('key', { _: 'Default' })` instead of `t('key')`
2. **Use semantic key names**: `products.landing.title` not `text1`
3. **Preview before syncing**: Run `preview_new_keys` first
4. **Batch appropriately**: Use batch_size=3 for small changes, larger for bulk updates
5. **Review in Lokalise**: Check translations in the dashboard after creating

## Support

For issues or questions:
- Check the [Installation Guide](INSTALLATION.md)
- Review error messages carefully
- Check Lokalise dashboard to verify keys were created

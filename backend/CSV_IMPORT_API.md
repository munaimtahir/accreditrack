# CSV Bulk Indicator Import System - API Documentation

## Overview

This document describes the CSV-based bulk indicator import system that allows administrators to upload a single CSV file and automatically create/update the complete compliance structure.

## Features

- ✅ CSV-based bulk import of indicators
- ✅ Automatic creation of Sections, Standards, and Indicators
- ✅ AI-powered frequency detection and normalization
- ✅ Idempotent imports (re-importing updates existing data)
- ✅ User assignment matching by email/username
- ✅ Upcoming tasks system for compliance tracking
- ✅ Support for one-time and recurring indicators
- ✅ Status tracking and history
- ✅ Evidence uploads

## CSV Format

The CSV file must have the following columns in exact order:

```csv
Section,Standard,Indicator,Evidence Required,Responsible Person,Frequency,Assigned to,Compliance Evidence,Score
```

### Column Descriptions

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| Section | Yes | Section/area name | "Academic Affairs" |
| Standard | Yes | Standard/regulation name | "Curriculum Standards" |
| Indicator | Yes | Indicator/requirement text | "All programs must have clearly defined learning outcomes" |
| Evidence Required | No | Description of required evidence | "Course syllabi with learning outcomes documented" |
| Responsible Person | No | Name of responsible person | "Dean of Academics" |
| Frequency | No | Frequency text (auto-detected) | "Annual", "Quarterly", "One time" |
| Assigned to | No | Email or username to assign | "dean@university.edu" |
| Compliance Evidence | No | Initial compliance notes | "Initial documentation complete" |
| Score | No | Score value (default: 10) | "15" |

### Example CSV

```csv
Section,Standard,Indicator,Evidence Required,Responsible Person,Frequency,Assigned to,Compliance Evidence,Score
Academic Affairs,Curriculum Standards,All programs must have clearly defined learning outcomes,Course syllabi with learning outcomes documented,Dean of Academics,One time,dean@university.edu,Initial documentation complete,10
Academic Affairs,Curriculum Standards,Regular curriculum review and updates,Committee meeting minutes and review reports,Curriculum Committee Chair,Annual,chair@university.edu,,15
Student Services,Admissions,Clear admission criteria published,Admission policy document and website screenshots,Admissions Director,Annual,admissions@university.edu,,10
```

## API Endpoints

### 1. Import CSV

**Endpoint:** `POST /api/projects/{project_id}/indicators/import-csv/`

**Authentication:** Required (Bearer token)

**Content-Type:** `multipart/form-data`

**Parameters:**
- `file`: CSV file to upload

**Example Request:**

```bash
curl -X POST \
  http://localhost:8000/api/projects/1/indicators/import-csv/ \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -F 'file=@indicators.csv'
```

**Example Response:**

```json
{
  "sections_created": 2,
  "standards_created": 3,
  "indicators_created": 15,
  "indicators_updated": 0,
  "rows_skipped": 0,
  "total_rows_processed": 15,
  "errors": [],
  "unmatched_users": ["dean@university.edu"]
}
```

**Error Response (Invalid Headers):**

```json
{
  "sections_created": 0,
  "standards_created": 0,
  "indicators_created": 0,
  "indicators_updated": 0,
  "rows_skipped": 0,
  "total_rows_processed": 0,
  "errors": [
    {
      "row": 0,
      "error": "Invalid CSV headers. Expected: Section, Standard, Indicator, Evidence Required, Responsible Person, Frequency, Assigned to, Compliance Evidence, Score"
    }
  ],
  "unmatched_users": []
}
```

### 2. Get Upcoming Tasks

**Endpoint:** `GET /api/projects/{project_id}/upcoming-tasks/`

**Authentication:** Required (Bearer token)

**Query Parameters:**
- `days_ahead` (optional): Number of days to look ahead (default: 30)

**Example Request:**

```bash
curl -X GET \
  'http://localhost:8000/api/projects/1/upcoming-tasks/?days_ahead=60' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

**Example Response:**

```json
[
  {
    "indicator_id": 123,
    "requirement": "Submit annual financial audit report",
    "section": "Administration",
    "standard": "Financial Management",
    "due_date": "2025-12-10",
    "is_overdue": true,
    "days_until_due": -9,
    "assigned_to": "cfo@university.edu",
    "status": "in_process",
    "schedule_type": "recurring",
    "frequency": "Annual"
  },
  {
    "indicator_id": 124,
    "requirement": "Update curriculum documentation",
    "section": "Academic Affairs",
    "standard": "Curriculum Standards",
    "due_date": "2025-12-25",
    "is_overdue": false,
    "days_until_due": 6,
    "assigned_to": "dean@university.edu",
    "status": "not_compliant",
    "schedule_type": "one_time",
    "frequency": ""
  }
]
```

### 3. Update Indicator Status

**Endpoint:** `POST /api/indicators/{indicator_id}/update-status/`

**Authentication:** Required (Bearer token)

**Content-Type:** `application/json`

**Request Body:**

```json
{
  "status": "compliant",
  "score": 15,
  "notes": "All documentation submitted and reviewed"
}
```

**Example Request:**

```bash
curl -X POST \
  http://localhost:8000/api/indicators/123/update-status/ \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "status": "compliant",
    "score": 15,
    "notes": "All documentation submitted and reviewed"
  }'
```

**Example Response:**

Returns the updated indicator object with all fields.

### 4. Upload Evidence

**Endpoint:** `POST /api/evidence/`

**Authentication:** Required (Bearer token)

**Content-Type:** `multipart/form-data`

**Parameters:**
- `indicator`: Indicator ID
- `title`: Evidence title
- `file`: Evidence file (optional)
- `url`: Evidence URL (optional)
- `notes`: Notes (optional)

**Example Request:**

```bash
curl -X POST \
  http://localhost:8000/api/evidence/ \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -F 'indicator=123' \
  -F 'title=Annual Audit Report 2025' \
  -F 'file=@audit_report.pdf' \
  -F 'notes=Completed by external auditor'
```

## Data Models

### Indicator Status Values

- `not_compliant` - Not Compliant (default)
- `in_process` - In Process
- `needs_more_evidence` - Needs More Evidence
- `compliant` - Compliant

### Schedule Types

- `one_time` - One-time requirement
- `recurring` - Recurring requirement

### Normalized Frequencies

- `Daily`
- `Weekly`
- `Bi-weekly`
- `Monthly`
- `Quarterly`
- `Semi-annually`
- `Annual`

## Import Behavior

### Section and Standard Creation

- **Case-insensitive matching**: "Academic Affairs" matches "academic affairs"
- **Automatic creation**: If section/standard doesn't exist, it's created
- **Reuse**: Existing sections/standards are reused across imports

### Indicator Idempotency

Each indicator has a unique `indicator_key` generated from:
```
SHA256(project_id:section_name:standard_name:indicator_text)
```

This ensures that re-importing the same CSV updates existing indicators instead of creating duplicates.

### Frequency Detection

The system uses AI and rule-based detection to determine:
1. **Schedule type**: One-time vs Recurring
2. **Normalized frequency**: Standardized frequency value

Frequency detection process:
1. Try rule-based detection (keywords like "daily", "monthly", etc.)
2. If confident (>80%), use rule-based result
3. Otherwise, call AI for analysis
4. If AI fails, fall back to rule-based or default

### User Assignment

The system attempts to match the "Assigned to" value with existing users:
1. First tries to match by email (case-insensitive)
2. Then tries to match by username (case-insensitive)
3. If no match found, stores the raw text in `assigned_to` field
4. Unmatched users are listed in the import response

## Upcoming Tasks Logic

### One-time Indicators

- Appear in upcoming tasks until status is `compliant`
- Use `next_due_date` if set, otherwise use `created_at` as due date

### Recurring Indicators

- Appear when due date is approaching or overdue
- Require a compliance log for each period
- Disappear after a compliant log is submitted for the current period
- Auto-calculate next due date based on frequency

### Task Sorting

Tasks are sorted by:
1. Overdue items first (highest priority)
2. Then by nearest due date (ascending)

## Error Handling

### Import Errors

The import process continues even if some rows fail. Each error is captured with:
- Row number
- Error message

This allows partial imports to succeed while reporting issues.

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Invalid CSV headers | Header mismatch | Ensure CSV has exact header order |
| Empty required fields | Missing Section/Standard/Indicator | Fill in all required columns |
| Invalid score | Non-numeric score value | Use valid integer for score |

## Best Practices

1. **Test with small CSV first**: Start with 5-10 rows to validate format
2. **Use consistent naming**: Keep section/standard names consistent across rows
3. **Specify frequencies clearly**: Use standard terms like "Monthly", "Annual"
4. **Include user emails**: Use actual user emails for automatic assignment
5. **Re-import for updates**: Same CSV can be imported multiple times safely
6. **Monitor unmatched users**: Check import response for users that couldn't be matched

## Security Considerations

- All endpoints require authentication
- File uploads are validated (CSV format only)
- Transaction-based imports (all-or-nothing per row)
- Evidence uploads linked to authenticated users
- Status changes tracked with user history

## Examples

See the example CSV file in `/tmp/test_indicators.csv` for a working example with various indicator types and frequencies.

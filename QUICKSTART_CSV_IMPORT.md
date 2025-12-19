# Quick Start Guide - CSV Bulk Indicator Import

## Prerequisites

1. AccrediFy backend running (Django server)
2. User account with authentication token
3. CSV file with compliance indicators

## Step-by-Step Guide

### Step 1: Prepare Your CSV File

Create a CSV file with this exact header order:

```csv
Section,Standard,Indicator,Evidence Required,Responsible Person,Frequency,Assigned to,Compliance Evidence,Score
```

**Example CSV** (`sample_indicators.csv`):

```csv
Section,Standard,Indicator,Evidence Required,Responsible Person,Frequency,Assigned to,Compliance Evidence,Score
Academic Affairs,Curriculum Standards,All programs must have clearly defined learning outcomes,Course syllabi with learning outcomes documented,Dean of Academics,One time,dean@university.edu,Initial documentation complete,10
Academic Affairs,Curriculum Standards,Regular curriculum review and updates,Committee meeting minutes and review reports,Curriculum Committee Chair,Annual,chair@university.edu,,15
Student Services,Admissions,Clear admission criteria published,Admission policy document and website screenshots,Admissions Director,Annual,admissions@university.edu,,10
Student Services,Admissions,Application processing within 30 days,Application tracking system reports,Admissions Director,Monthly,admissions@university.edu,,10
Facilities,Safety & Security,Emergency evacuation plans posted,Photos of posted evacuation maps,Facilities Manager,Annual,facilities@university.edu,,10
Facilities,Safety & Security,Fire safety equipment inspection,Inspection certificates and maintenance logs,Safety Officer,Quarterly,safety@university.edu,,15
```

### Step 2: Get Your Authentication Token

```bash
# Login to get token
curl -X POST http://localhost:8000/api/token/ \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'

# Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

# Save the access token
export TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Step 3: Create a Project (if needed)

```bash
curl -X POST http://localhost:8000/api/projects/ \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "University Accreditation 2025",
    "description": "Annual accreditation compliance tracking"
  }'

# Response:
{
  "id": 1,
  "name": "University Accreditation 2025",
  "description": "Annual accreditation compliance tracking",
  "created_at": "2025-12-19T10:00:00Z",
  "updated_at": "2025-12-19T10:00:00Z",
  "indicators_count": 0,
  "sections_count": 0
}
```

### Step 4: Import Your CSV File

```bash
curl -X POST http://localhost:8000/api/projects/1/indicators/import-csv/ \
  -H "Authorization: Bearer $TOKEN" \
  -F 'file=@sample_indicators.csv'

# Response:
{
  "sections_created": 3,
  "standards_created": 4,
  "indicators_created": 6,
  "indicators_updated": 0,
  "rows_skipped": 0,
  "total_rows_processed": 6,
  "errors": [],
  "unmatched_users": [
    "dean@university.edu",
    "chair@university.edu",
    "admissions@university.edu",
    "facilities@university.edu",
    "safety@university.edu"
  ]
}
```

**Success!** Your compliance structure is now created:
- 3 Sections
- 4 Standards
- 6 Indicators

### Step 5: View Upcoming Tasks

```bash
curl -X GET "http://localhost:8000/api/projects/1/upcoming-tasks/?days_ahead=90" \
  -H "Authorization: Bearer $TOKEN"

# Response:
[
  {
    "indicator_id": 1,
    "requirement": "All programs must have clearly defined learning outcomes",
    "section": "Academic Affairs",
    "standard": "Curriculum Standards",
    "due_date": "2025-12-19",
    "is_overdue": false,
    "days_until_due": 0,
    "assigned_to": "dean@university.edu",
    "status": "not_compliant",
    "schedule_type": "one_time",
    "frequency": ""
  },
  {
    "indicator_id": 2,
    "requirement": "Regular curriculum review and updates",
    "section": "Academic Affairs",
    "standard": "Curriculum Standards",
    "due_date": "2026-12-19",
    "is_overdue": false,
    "days_until_due": 365,
    "assigned_to": "chair@university.edu",
    "status": "not_compliant",
    "schedule_type": "recurring",
    "frequency": "Annual"
  }
]
```

### Step 6: Update Indicator Status

```bash
curl -X POST http://localhost:8000/api/indicators/1/update-status/ \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "status": "compliant",
    "score": 10,
    "notes": "All course syllabi reviewed and approved"
  }'

# Response: Full indicator object with updated status
```

### Step 7: Upload Evidence

```bash
curl -X POST http://localhost:8000/api/evidence/ \
  -H "Authorization: Bearer $TOKEN" \
  -F 'indicator=1' \
  -F 'title=Course Syllabi Collection' \
  -F 'file=@syllabi.pdf' \
  -F 'notes=All program syllabi compiled and reviewed'

# Response:
{
  "id": 1,
  "indicator": 1,
  "title": "Course Syllabi Collection",
  "file": "/media/evidence/syllabi.pdf",
  "url": "",
  "notes": "All program syllabi compiled and reviewed",
  "uploaded_by": 1,
  "uploaded_by_name": "admin",
  "uploaded_at": "2025-12-19T10:15:00Z"
}
```

### Step 8: Re-Import to Update

If you need to update indicators, just re-import the same CSV with modifications:

```bash
# Modify your CSV (change frequencies, add notes, etc.)
# Then re-import
curl -X POST http://localhost:8000/api/projects/1/indicators/import-csv/ \
  -H "Authorization: Bearer $TOKEN" \
  -F 'file=@sample_indicators_updated.csv'

# Response:
{
  "sections_created": 0,
  "standards_created": 0,
  "indicators_created": 0,
  "indicators_updated": 6,  # All existing indicators updated
  "rows_skipped": 0,
  "total_rows_processed": 6,
  "errors": [],
  "unmatched_users": [...]
}
```

## Common Use Cases

### Use Case 1: Initial Setup
1. Prepare comprehensive CSV with all compliance indicators
2. Import CSV to create complete structure
3. Review upcoming tasks
4. Assign team members to tasks

### Use Case 2: Quarterly Update
1. Update CSV with new indicators or modified frequencies
2. Re-import CSV (existing indicators update, new ones create)
3. Review changes in upcoming tasks
4. Track status updates

### Use Case 3: Status Tracking
1. Team members complete compliance tasks
2. Upload evidence for each indicator
3. Update indicator status to "compliant"
4. System automatically removes from upcoming tasks (one-time) or tracks next period (recurring)

## Tips for Success

1. **Start Small**: Import 5-10 indicators first to verify format
2. **Use Standard Frequencies**: "Daily", "Weekly", "Monthly", "Quarterly", "Annual"
3. **Keep Consistent Naming**: Use exact same section/standard names across rows
4. **Monitor Unmatched Users**: Create user accounts for emails that don't match
5. **Check Upcoming Tasks**: Verify indicators appear correctly with proper due dates

## Troubleshooting

### Error: Invalid CSV headers
**Solution**: Ensure your CSV has the exact headers in this order:
```
Section,Standard,Indicator,Evidence Required,Responsible Person,Frequency,Assigned to,Compliance Evidence,Score
```

### Error: Row skipped - Required fields empty
**Solution**: Ensure every row has values for Section, Standard, and Indicator columns

### Warning: Unmatched users
**Not an error**: The system stores the email/username as text. Create user accounts later and they'll be automatically linked on next import.

### Indicators not in upcoming tasks
**Check**: 
- Is indicator active? (`is_active` should be True)
- Is it compliant? (One-time compliant indicators don't show in tasks)
- Is it within date range? (Default is 30 days ahead)

## API Reference

Full API documentation available in: `backend/CSV_IMPORT_API.md`

## Support

For issues or questions:
1. Check the error message in the import response
2. Review the API documentation
3. Check Django admin for detailed indicator information
4. Verify CSV format matches the template

## Example CSV Templates

Available in the repository:
- `/tmp/test_indicators.csv` - Comprehensive example with various frequencies
- Create your own based on the format above

## Next Steps

After successful import:
1. Review the admin interface to see created structure
2. Monitor upcoming tasks regularly
3. Train team on status updates and evidence uploads
4. Set up periodic re-imports for compliance updates

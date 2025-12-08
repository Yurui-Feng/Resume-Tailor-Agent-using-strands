# Data: TailorResult

Result metadata from resume tailoring.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `tex_path` | string | Path to generated .tex file |
| `pdf_path` | string | Path to generated .pdf file (if rendered) |
| `company` | string | Extracted/provided company name |
| `position` | string | Extracted/provided job position |
| `validation` | object | LaTeX validation results |

## File Naming Convention

```
{Company}_{Position}_{Timestamp}.tex
{Company}_{Position}_{Timestamp}.pdf
```

Example: `Google_Senior_ML_Engineer_20250107_143052.pdf`

## Storage Location

- `data/tailored_resumes/` - All generated files

## Source

`backend/api/models.py:91`

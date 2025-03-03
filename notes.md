# Backend TODOs for Completing Payment Page Functionality

## 1. OneDrive Integration Issues
The current implementation uses a placeholder temp directory for file storage, but needs proper OneDrive integration.

**Evidence:** In `/backend/services/file_service.py`, the `get_onedrive_root_path()` function tries to detect OneDrive folders but falls back to a temporary directory:
```python
# For development/testing, return a temp directory
return Path(os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_onedrive"))
```

**TODO:** Implement proper OneDrive path detection/integration for Windows systems. This might require testing on actual Windows environment to ensure correct paths are detected.

## 2. Missing Client Metrics Implementation
The `client_metrics` table is defined in the schema but there's no implementation for updating it when payments are added or modified.

**Evidence:** The database schema contains a `client_metrics` table and `frontend/app/page.tsx` will likely need this data for the client snapshot section, but there's no implementation to maintain this table when payments change.

**TODO:** Implement functions to update client metrics when payments are created/updated/deleted. This should include:
- Calculating last payment details
- Tracking YTD payments
- Calculating average quarterly payment
- Tracking last recorded AUM

## 3. Complete Expected Fee Calculation
The expected fee calculation needs to account for all fee structures (flat, percentage) and handle display on the frontend.

**Evidence:** Current implementation in `payment_service.py` has good foundations but might need refinement to match the required display format in the payment entry panel:
```
- Expected Fee (calculated as: AUM * rate): $[calculated]
- Payment Variance: $[difference] ([percentage]%)
- Color indicator: green (within 5%), yellow (5-15%), red (>15%)
```

**TODO:** Enhance `calculate_expected_fee` to include variance calculation and percentage difference to support frontend color coding.

## 4. Split Payment UI Support
While split payment functionality exists in the backend, there needs to be additional API endpoints to support the UI requirements.

**Evidence:** The code shows split payment creation and management, but endpoints are needed to calculate evenly distributed amounts for frontend display before submission:
```
- Applied Period(s): Shows selected month(s)/quarter(s) the payment will cover.
- Example: "Applied Period(s): JAN 1 2020: $1,000.00 | FEB 1 2020: $1,000.00 | Total: $2,000.00"
```

**TODO:** Add API endpoint to preview split payment distribution before submission.

## 5. File Preview System
The current file handling system needs enhancement to support document preview functionality.

**Evidence:** The blueprint describes an expandable panel for document viewing with:
```
PREVIEW:
- Large preview pane showing selected document
- Next/previous buttons to navigate between files
- Toggle for side-by-side comparison (up to two files)
- Supports PDF, images, Office documents, text files
```

**TODO:** Enhance the file content endpoint to support more document types and preview modes.

## 6. Client Document Tree View
File system integration needs enhancement to support folder-tree structure for client documents.

**Evidence:** The requirements specify:
```
NAVIGATION:
- Folder-tree structure displaying files from client's OneDrive root folder
- Single-click folders to expand/collapse
```

**TODO:** Add API endpoints to retrieve folder-tree structure from OneDrive for client documents.

## 7. Testing of File Upload/Download Workflows
The file upload/download endpoints are implemented but need thorough testing.

**Evidence:** File endpoints exist but there's uncertainty about how they'll work with actual OneDrive storage.

**TODO:** Test file operations end-to-end to ensure proper integration with OneDrive.

## 8. Contract Details Retrieval
API endpoint is needed for easy retrieval of all contract details when selecting a client.

**Evidence:** Contract details are needed for payment entry and validation, but there's no dedicated endpoint to get just the active contract for a client.

**TODO:** Add a specific endpoint to get the active contract for a client if multiple contracts exist.

---

All these TODOs are reasonable steps to complete the backend for the payment page functionality without introducing unnecessary complications. They address direct requirements from the blueprint while ensuring the core functionality works correctly.



----


# FILE SYSTEM ATTEMPTED 
  1. We've completely rewritten the file system service to work with your actual file structure:
    - Used a configurable shared folder path that adapts to different user environments
    - Implemented scanning of existing directories to find and register files
    - Added support for both client document directories and payment-specific folders
  2. We've enhanced the file handling capabilities:
    - Added ability to scan directories and register existing files
    - Improved path handling to work with your shared OneDrive structure
    - Implemented folder structure discovery
  3. We've added client folder path management:
    - Added ability to update a client's folder path in the database
    - Created endpoints to configure the shared paths

  These changes make the backend capable of working with your actual file structure, rather than trying to create a parallel structure.       
  The system will now:

  1. Scan and recognize existing files in your "401Ks\Current PlansCLIENT_NAME}" folders
  2. Store relative paths in the database that will work for any user on the system
  3. Adapt to different user environments automatically by detecting the correct path to the shared folder

  This provides a solid foundation for the payment page's document handling requirements and prepares the system for future enhancements. 
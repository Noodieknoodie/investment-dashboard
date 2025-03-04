# Backend TODOs for Completing Payment Page Functionality


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




  ---


  ● Let's summarize the changes we made:

  1. Fixed the API endpoint mismatch:
    - Changed the frontend API call from /payments/calculate-fee to /payments/expected-fee to match the backend endpoint.
  2. Fixed the year calculation bug in payment_service.py:
    - In the get_available_periods function, updated the year calculation to use integer division (//) instead of assignment.
    - Fixed this in both the monthly and quarterly period calculation sections.

  These changes should resolve the "error failed to load available payments" issue that was occurring on app launch.

  The root cause was that the frontend was trying to call an endpoint (/payments/calculate-fee) that didn't exist in the backend. The        
  backend had implemented the endpoint as /payments/expected-fee.

  Additionally, we fixed the year calculation bug that could potentially cause incorrect period calculations.
# DB Insights for 401(k) Payment Tracking System

## Table: quarterly_summaries
- **Row Count**: 493
- **Column Analysis**:
  - **id**: INTEGER | range: 1-493
  - **client_id**: INTEGER NOT NULL | range: 1-49
  - **year**: INTEGER NOT NULL | range: 1900-2024
  - **quarter**: INTEGER NOT NULL | range: 1-4
  - **total_payments**: REAL | range: $22-$907613413
  - **total_assets**: REAL | range: $0-$7967471978
  - **payment_count**: INTEGER | range: 1-20
  - **avg_payment**: REAL | range: $8-$50422967
  - **expected_total**: REAL | range: 0.0-46875.0
  - **last_updated**: TEXT | format: YYYY-MM-DD | values: [2025-02-27 08:45:17]

## Table: yearly_summaries
- **Row Count**: 145
- **Column Analysis**:
  - **id**: INTEGER | range: 1-145
  - **client_id**: INTEGER NOT NULL | range: 1-49
  - **year**: INTEGER NOT NULL | range: 1900-2024
  - **total_payments**: REAL | range: $22-$907748413
  - **total_assets**: REAL | range: $8971-$2009867994
  - **payment_count**: INTEGER | range: 1-23
  - **avg_payment**: REAL | range: $8-$12639491
  - **yoy_growth**: REAL | range: 0-0
  - **last_updated**: TEXT | format: YYYY-MM-DD | values: [2025-02-27 08:45:17]

## Table: contacts
- **Row Count**: 70
- **Contact Types**: ['Primary', 'Authorized', 'Provider', 'Billing']
- **Column Analysis**:
  - **contact_id**: INTEGER | range: 1-90
  - **client_id**: INTEGER NOT NULL | range: 1-49
  - **contact_type**: TEXT NOT NULL | values: [Primary, Authorized, Provider, Billing]
  - **contact_name**: TEXT | unique values: 59
  - **phone**: TEXT | phone | unique values: 32
  - **email**: TEXT | email | unique values: 48
  - **fax**: TEXT | values: [555-987-6543, 866-377-9577 , 206-433-0280]
  - **physical_address**: TEXT | unique values: 29
  - **mailing_address**: TEXT | unique values: 18
  - **valid_from**: DATETIME
  - **valid_to**: DATETIME

## Table: contracts
- **Row Count**: 36
- **Payment Schedules**: ['monthly', 'quarterly'] (47/52% split)
- **Fee Types**: ['Percentage', 'flat', 'percentage'] (2/37/60% split)
- **Top Providers**: ['John Hancock', 'Voya', 'Empower', 'Fidelity', 'Nationwide']
- **Column Analysis**:
  - **contract_id**: INTEGER NOT NULL | range: 1-39
  - **client_id**: INTEGER NOT NULL | range: 1-49
  - **contract_number**: TEXT | unique values: 26
  - **provider_name**: TEXT | unique values: 16
  - **contract_start_date**: TEXT | format: YYYY-MM-DD | values: [2024-01-01, 2019-05-2019, 2019-04-19, 2018-03-22]
  - **fee_type**: TEXT | values: [percentage, flat, Percentage]
  - **percent_rate**: REAL | range: 0.0%-0.75%
  - **flat_rate**: REAL | range: 666.66-6250.0
  - **payment_schedule**: TEXT | values: [quarterly, monthly]
  - **num_people**: INTEGER | range: 2-531
  - **notes**: TEXT | values: [Phone: 800-333-0963 Option 1 with Contract # or Option 2, ext 154617
Fax: General Info 866-377-9577  Enrollment Forms 866-377-8846 
, Mock test contract for AA_TEST client]
  - **valid_from**: DATETIME
  - **valid_to**: DATETIME

## Table: client_metrics
- **Row Count**: 30
- **Column Analysis**:
  - **id**: INTEGER NOT NULL | range: 1-30
  - **client_id**: INTEGER NOT NULL | range: 1-49
  - **last_payment_date**: TEXT | format: YYYY-MM-DD | unique values: 13
  - **last_payment_amount**: REAL | range: $39-$12150
  - **last_payment_quarter**: INTEGER | range: 1-4
  - **last_payment_year**: INTEGER | range: 2023-2024 | values: [2023, 2024]
  - **total_ytd_payments**: REAL | range: $0-$0
  - **avg_quarterly_payment**: REAL | range: $0-$0
  - **last_recorded_assets**: REAL | range: $56262-$15397306
  - **last_updated**: TEXT | format: YYYY-MM-DD | values: [2025-02-27 08:45:17]

## Table: payments
- **Row Count**: 952
- **Payment Methods**: ['Auto - Check', 'Auto - ACH', 'Invoice - Check', 'None Specified', 'Wire Transfer', 'Check']
- **Column Analysis**:
  - **payment_id**: INTEGER NOT NULL | range: 1-976
  - **contract_id**: INTEGER NOT NULL | range: 1-39
  - **client_id**: INTEGER NOT NULL | range: 1-49
  - **received_date**: TEXT | format: YYYY-MM-DD | unique values: 366
  - **total_assets**: INTEGER | range: 33-0
  - **expected_fee**: REAL | range: $0-$46875
  - **actual_fee**: REAL | range: $3-$861111111
  - **method**: TEXT | values: [Auto - Check, Auto - ACH, Invoice - Check, None Specified, Wire Transfer, Check]
  - **notes**: TEXT | unique values: 125
  - **split_group_id**: TEXT
  - **valid_from**: DATETIME
  - **valid_to**: DATETIME
  - **applied_start_month**: INTEGER | range: 1-12
  - **applied_start_month_year**: INTEGER | range: 2019-2024
  - **applied_end_month**: INTEGER | range: 1-12
  - **applied_end_month_year**: INTEGER | range: 2019-2024
  - **applied_start_quarter**: INTEGER | range: 1-4
  - **applied_start_quarter_year**: INTEGER | range: 2019-2024
  - **applied_end_quarter**: INTEGER | range: 1-4
  - **applied_end_quarter_year**: INTEGER | range: 2019-2024

## Table: clients
- **Row Count**: 30
- **Column Analysis**:
  - **client_id**: INTEGER NOT NULL | range: 1-49
  - **display_name**: TEXT NOT NULL | unique values: 30
  - **full_name**: TEXT | unique values: 30
  - **ima_signed_date**: TEXT | format: YYYY-MM-DD | unique values: 19
  - **onedrive_folder_path**: TEXT | values: [/documentation/AA_TEST/]
  - **valid_from**: DATETIME
  - **valid_to**: DATETIME

## Table: client_files
- **Row Count**: 0
- **Common Extensions**: []
- **Column Analysis**:
  - **file_id**: INTEGER NOT NULL
  - **client_id**: INTEGER NOT NULL
  - **file_name**: TEXT NOT NULL
  - **onedrive_path**: TEXT NOT NULL
  - **uploaded_at**: DATETIME

## Table: payment_files
- **Row Count**: 0
- **Column Analysis**:
  - **payment_id**: INTEGER NOT NULL
  - **file_id**: INTEGER NOT NULL
  - **linked_at**: DATETIME

## Common Edge Cases
- Empty total_assets when fee_type='Fixed'
- Split payments spanning year boundaries
- Clients with changed fee structures mid-year
- Multi-quarter payments (Q2-Q4 together)
- Backdated payments (received_date > 60 days after period end)
- Files with same name in different client folders

## General Guidelines
- Always handle NULL in optional fields (total_assets, method, notes)
- Convert dates with datetime.strptime/strftime using 'YYYY-MM-DD' format
- Format currency with locale.currency() for display
- Payment period calculations: Use supplied AUM*rate if available, otherwise last known AUM*rate
- Store decimal values with Decimal() not float for financial calculations

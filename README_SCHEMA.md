============================
SQLite SCHEMA -- FOR REFERENCE (Remember: the database is already created with the schema and populated with data, and will reside in the project directory)
============================

CREATE TABLE sqlite_sequence(name,seq)
CREATE TABLE quarterly_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    total_payments REAL,
    total_assets REAL,
    payment_count INTEGER,
    avg_payment REAL,
    expected_total REAL,
    last_updated TEXT,
    FOREIGN KEY(client_id) REFERENCES clients(client_id) ON DELETE CASCADE,
    UNIQUE(client_id, year, quarter)
)
CREATE TABLE yearly_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    total_payments REAL,
    total_assets REAL,
    payment_count INTEGER,
    avg_payment REAL,
    yoy_growth REAL,
    last_updated TEXT,
    FOREIGN KEY(client_id) REFERENCES clients(client_id) ON DELETE CASCADE,
    UNIQUE(client_id, year)
)
CREATE TABLE contacts (
    contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    contact_type TEXT NOT NULL,
    contact_name TEXT,
    phone TEXT,
    email TEXT,
    fax TEXT,
    physical_address TEXT,
    mailing_address TEXT,
    valid_from DATETIME DEFAULT CURRENT_TIMESTAMP,
    valid_to DATETIME,
    FOREIGN KEY(client_id) REFERENCES clients(client_id) ON DELETE CASCADE
)
CREATE INDEX idx_quarterly_lookup ON quarterly_summaries(client_id, year, quarter)
CREATE INDEX idx_yearly_lookup ON yearly_summaries(client_id, year)
CREATE INDEX idx_contacts_client_id ON contacts(client_id)
CREATE INDEX idx_contacts_type ON contacts(client_id, contact_type)
CREATE TABLE "contracts" (
    "contract_id"    INTEGER NOT NULL,
    "client_id"    INTEGER NOT NULL,
    "contract_number"    TEXT,
    "provider_name"    TEXT,
    "contract_start_date"    TEXT,
    "fee_type"    TEXT,
    "percent_rate"    REAL,
    "flat_rate"    REAL,
    "payment_schedule"    TEXT,
    "num_people"    INTEGER,
    "notes"    TEXT,
    "valid_from"    DATETIME DEFAULT CURRENT_TIMESTAMP,
    "valid_to"    DATETIME,
    PRIMARY KEY("contract_id" AUTOINCREMENT),
    FOREIGN KEY("client_id") REFERENCES "clients"("client_id") ON DELETE CASCADE
)
CREATE INDEX idx_contracts_client_id ON contracts(client_id)
CREATE INDEX idx_contracts_provider ON contracts(provider_name)
CREATE TABLE "client_metrics" (
    "id"    INTEGER NOT NULL,
    "client_id"    INTEGER NOT NULL,
    "last_payment_date"    TEXT,
    "last_payment_amount"    REAL,
    "last_payment_quarter"    INTEGER,
    "last_payment_year"    INTEGER,
    "total_ytd_payments"    REAL,
    "avg_quarterly_payment"    REAL,
    "last_recorded_assets"    REAL,
    "last_updated"    TEXT,
    UNIQUE("client_id"),
    PRIMARY KEY("id" AUTOINCREMENT),
    FOREIGN KEY("client_id") REFERENCES "clients"("client_id") ON DELETE CASCADE
)
CREATE INDEX idx_client_metrics_lookup ON client_metrics(client_id)
CREATE TRIGGER update_yearly_after_quarterly
    AFTER INSERT ON quarterly_summaries
    BEGIN
        INSERT OR REPLACE INTO yearly_summaries 
        (client_id, year, total_payments, total_assets, payment_count, avg_payment, yoy_growth, last_updated)
        SELECT 
            client_id, 
            year, 
            SUM(total_payments), 
            AVG(total_assets), 
            SUM(payment_count), 
            AVG(avg_payment),
            NULL,
            datetime('now')
        FROM quarterly_summaries 
        WHERE client_id = NEW.client_id 
            AND year = NEW.year
        GROUP BY client_id, year;
    END
CREATE TABLE "payments" (
    "payment_id"    INTEGER NOT NULL,
    "contract_id"    INTEGER NOT NULL,
    "client_id"    INTEGER NOT NULL,
    "received_date"    TEXT,
    "total_assets"    INTEGER,
    "expected_fee"    REAL,
    "actual_fee"    REAL,
    "method"    TEXT,
    "notes"    TEXT,
    "split_group_id"    TEXT,
    "valid_from"    DATETIME DEFAULT CURRENT_TIMESTAMP,
    "valid_to"    DATETIME,
    "applied_start_month"    INTEGER,
    "applied_start_month_year"    INTEGER,
    "applied_end_month"    INTEGER,
    "applied_end_month_year"    INTEGER,
    "applied_start_quarter"    INTEGER,
    "applied_start_quarter_year"    INTEGER,
    "applied_end_quarter"    INTEGER,
    "applied_end_quarter_year"    INTEGER,
    PRIMARY KEY("payment_id" AUTOINCREMENT),
    FOREIGN KEY("client_id") REFERENCES "clients"("client_id") ON DELETE CASCADE,
    FOREIGN KEY("contract_id") REFERENCES "contracts"("contract_id") ON DELETE CASCADE
)
CREATE INDEX idx_payments_client_id ON payments(client_id)
CREATE INDEX idx_payments_contract_id ON payments(contract_id)
CREATE INDEX idx_payments_date ON payments(client_id, received_date DESC)
CREATE INDEX idx_payments_split_group ON payments(split_group_id)
CREATE TRIGGER update_quarterly_after_payment
AFTER INSERT ON payments
BEGIN
    INSERT OR REPLACE INTO quarterly_summaries 
    (client_id, year, quarter, total_payments, total_assets, payment_count, avg_payment, expected_total, last_updated)
    SELECT 
        client_id, 
        applied_start_quarter_year, 
        applied_start_quarter, 
        SUM(actual_fee), 
        AVG(total_assets), 
        COUNT(*), 
        AVG(actual_fee), 
        MAX(expected_fee), 
        datetime('now')
    FROM payments 
    WHERE client_id = NEW.client_id 
      AND applied_start_quarter_year = NEW.applied_start_quarter_year 
      AND applied_start_quarter = NEW.applied_start_quarter
    GROUP BY client_id, applied_start_quarter_year, applied_start_quarter;
END
CREATE TABLE "clients" (
    "client_id"    INTEGER NOT NULL,
    "display_name"    TEXT NOT NULL,
    "full_name"    TEXT,
    "ima_signed_date"    TEXT,
    "onedrive_folder_path"    TEXT,
    "valid_from"    DATETIME DEFAULT CURRENT_TIMESTAMP,
    "valid_to"    DATETIME,
    PRIMARY KEY("client_id" AUTOINCREMENT)
)
CREATE TABLE "client_files" (
    "file_id" INTEGER NOT NULL,
    "client_id" INTEGER NOT NULL,
    "file_name" TEXT NOT NULL,
    "onedrive_path" TEXT NOT NULL,
    "uploaded_at" DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY("file_id" AUTOINCREMENT),
    FOREIGN KEY("client_id") REFERENCES "clients"("client_id") ON DELETE CASCADE
)
CREATE TABLE "payment_files" (
    "payment_id" INTEGER NOT NULL,
    "file_id" INTEGER NOT NULL,
    "linked_at" DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY("payment_id", "file_id"),
    FOREIGN KEY("payment_id") REFERENCES "payments"("payment_id") ON DELETE CASCADE,
    FOREIGN KEY("file_id") REFERENCES "client_files"("file_id") ON DELETE CASCADE
)

```
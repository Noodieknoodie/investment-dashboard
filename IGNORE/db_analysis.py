import sqlite3
import os
import re
from datetime import datetime

def safe_fetch_one(cursor, default=None):
    """Safely fetch one row, returning default if None."""
    result = cursor.fetchone()
    return result if result is not None else default

def safe_fetch_all(cursor, default=None):
    """Safely fetch all rows, returning default if None."""
    result = cursor.fetchall()
    return result if result is not None else default or []

def safe_get(obj, key, default=None):
    """Safely get a value from a dict or list."""
    if obj is None:
        return default
    try:
        return obj[key]
    except (IndexError, KeyError, TypeError):
        return default

def safe_number(value, default=0):
    """Safely convert a value to a number, with fallback to default."""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    """Safely convert a value to an integer, with fallback to default."""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_round(value, digits=1, default=0):
    """Safely round a value, with fallback to default."""
    if value is None:
        return default
    try:
        return round(float(value), digits)
    except (ValueError, TypeError):
        return default

def safe_execute(cursor, query, default=None):
    """Safely execute a query, returning default on error."""
    try:
        cursor.execute(query)
        return True
    except sqlite3.Error as e:
        print(f"Database error executing: {query}")
        print(f"Error: {e}")
        return default

def analyze_database(db_path, output_path):
    """Analyze every field of every table in the 401k DB and generate concise insights."""
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all tables
        if not safe_execute(cursor, "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
            raise Exception("Could not get table list from database")
        
        tables_result = safe_fetch_all(cursor, [])
        tables = [safe_get(row, 0, "") for row in tables_result if row is not None]
        tables = [t for t in tables if t]  # Filter out empty table names
        
        print(f"Found {len(tables)} tables: {', '.join(tables)}")
        
        insights = {}
        
        # Analyze each table
        for table in tables:
            print(f"Analyzing table: {table}")
            insights[table] = {}
            
            # Basic table stats
            if not safe_execute(cursor, f"SELECT COUNT(*) FROM '{table}'"):
                print(f"Could not get row count for table {table}, skipping")
                continue
                
            row_result = safe_fetch_one(cursor, [0])
            row_count = safe_get(row_result, 0, 0)
            insights[table]['row_count'] = row_count
            
            # Get column info
            if not safe_execute(cursor, f"PRAGMA table_info('{table}')"):
                print(f"Could not get column info for table {table}, skipping")
                continue
                
            columns_result = safe_fetch_all(cursor, [])
            column_insights = {}
            
            for col in columns_result:
                if col is None:
                    continue
                    
                col_name = safe_get(col, 1, "unknown")
                col_type = safe_get(col, 2, "").upper()
                not_null = safe_get(col, 3, 0) == 1
                
                col_data = {}
                col_data['type'] = col_type
                col_data['nullable'] = not not_null
                
                # Skip analysis for empty tables
                if row_count == 0:
                    col_data['null_count'] = 0
                    col_data['null_percent'] = 0
                    column_insights[col_name] = col_data
                    continue
                
                # Calculate NULL percentage
                if not safe_execute(cursor, f"SELECT COUNT(*) FROM '{table}' WHERE '{col_name}' IS NULL"):
                    col_data['null_count'] = "error"
                    col_data['null_percent'] = "error"
                    column_insights[col_name] = col_data
                    continue
                    
                null_result = safe_fetch_one(cursor, [0])
                null_count = safe_get(null_result, 0, 0)
                col_data['null_count'] = null_count
                col_data['null_percent'] = safe_round((null_count / row_count) * 100 if row_count > 0 else 0)
                
                # Skip further analysis if all values are NULL
                if null_count == row_count:
                    column_insights[col_name] = col_data
                    continue
                
                # Analyze based on column type
                try:
                    if 'INT' in col_type:
                        if not safe_execute(cursor, f"SELECT MIN({col_name}), MAX({col_name}), AVG({col_name}) FROM '{table}' WHERE {col_name} IS NOT NULL"):
                            col_data['error'] = "Could not get min/max/avg"
                            column_insights[col_name] = col_data
                            continue
                            
                        stat_result = safe_fetch_one(cursor, [None, None, None])
                        min_val = safe_get(stat_result, 0)
                        max_val = safe_get(stat_result, 1)
                        avg_val = safe_get(stat_result, 2)
                        
                        col_data['min'] = safe_int(min_val)
                        col_data['max'] = safe_int(max_val)
                        col_data['avg'] = safe_round(avg_val)
                        
                        # Check for common 0/1 boolean pattern
                        if safe_execute(cursor, f"SELECT COUNT(DISTINCT {col_name}) FROM '{table}' WHERE {col_name} IS NOT NULL"):
                            distinct_result = safe_fetch_one(cursor, [0])
                            distinct_count = safe_get(distinct_result, 0, 0)
                            
                            if distinct_count <= 2:
                                if safe_execute(cursor, f"SELECT {col_name}, COUNT(*) FROM '{table}' WHERE {col_name} IS NOT NULL GROUP BY {col_name}"):
                                    value_results = safe_fetch_all(cursor, [])
                                    values = {str(safe_get(row, 0, "")): safe_get(row, 1, 0) for row in value_results if row is not None}
                                    col_data['values'] = values
                                    if set(map(str, values.keys())) == {'0', '1'}:
                                        col_data['appears_boolean'] = True
                        
                    elif 'REAL' in col_type or 'FLOAT' in col_type or 'DOUBLE' in col_type or 'DECIMAL' in col_type:
                        if not safe_execute(cursor, f"SELECT MIN({col_name}), MAX({col_name}), AVG({col_name}) FROM '{table}' WHERE {col_name} IS NOT NULL"):
                            col_data['error'] = "Could not get min/max/avg"
                            column_insights[col_name] = col_data
                            continue
                            
                        stat_result = safe_fetch_one(cursor, [None, None, None])
                        min_val = safe_get(stat_result, 0)
                        max_val = safe_get(stat_result, 1)
                        avg_val = safe_get(stat_result, 2)
                        
                        col_data['min'] = safe_round(min_val, 2)
                        col_data['max'] = safe_round(max_val, 2)
                        col_data['avg'] = safe_round(avg_val, 2)
                        
                        # Check if values look like percentages
                        if safe_number(max_val) <= 1.0 and col_name.lower().find('rate') >= 0:
                            col_data['appears_percentage'] = True
                        
                        # Check if values look like currency
                        if safe_number(min_val) >= 0 and (col_name.lower().find('fee') >= 0 or 
                                                        col_name.lower().find('amount') >= 0 or
                                                        col_name.lower().find('assets') >= 0 or
                                                        col_name.lower().find('payment') >= 0):
                            col_data['appears_currency'] = True
                    
                    elif 'TEXT' in col_type or 'VARCHAR' in col_type or 'CHAR' in col_type:
                        # Get distinct value count
                        if safe_execute(cursor, f"SELECT COUNT(DISTINCT {col_name}) FROM '{table}' WHERE {col_name} IS NOT NULL"):
                            distinct_result = safe_fetch_one(cursor, [0])
                            distinct_count = safe_get(distinct_result, 0, 0)
                            col_data['distinct_count'] = distinct_count
                            
                            # If low cardinality field, get all values and counts
                            if 1 <= distinct_count <= 15 and row_count > 0:
                                if safe_execute(cursor, f"SELECT {col_name}, COUNT(*) FROM '{table}' WHERE {col_name} IS NOT NULL GROUP BY {col_name} ORDER BY COUNT(*) DESC"):
                                    value_results = safe_fetch_all(cursor, [])
                                    values = {str(safe_get(row, 0, "")): safe_get(row, 1, 0) for row in value_results if row is not None}
                                    col_data['values'] = values
                        
                        # Get a sample value for format analysis
                        if safe_execute(cursor, f"SELECT {col_name} FROM '{table}' WHERE {col_name} IS NOT NULL LIMIT 1"):
                            sample_result = safe_fetch_one(cursor)
                            sample_value = safe_get(sample_result, 0) if sample_result else None
                            
                            # Detect date format
                            if sample_value and isinstance(sample_value, str):
                                if re.match(r'\d{4}-\d{2}-\d{2}', sample_value):
                                    col_data['appears_date'] = True
                                    col_data['format'] = 'YYYY-MM-DD'
                                elif re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', sample_value):
                                    col_data['appears_date'] = True
                                    col_data['format'] = 'YYYY-MM-DD HH:MM:SS'
                            
                            # Check if email field
                            if col_name.lower() == 'email' and sample_value and isinstance(sample_value, str) and '@' in sample_value:
                                col_data['appears_email'] = True
                            
                            # Check if phone field
                            if col_name.lower() in ['phone', 'telephone', 'phone_number'] and sample_value and isinstance(sample_value, str):
                                col_data['appears_phone'] = True
                    
                    elif 'DATE' in col_type or 'TIME' in col_type:
                        col_data['is_date'] = True
                        
                        # Get date range
                        if safe_execute(cursor, f"SELECT MIN({col_name}), MAX({col_name}) FROM '{table}' WHERE {col_name} IS NOT NULL"):
                            date_result = safe_fetch_one(cursor, [None, None])
                            min_date = safe_get(date_result, 0)
                            max_date = safe_get(date_result, 1)
                            
                            if min_date and max_date:
                                col_data['min_date'] = str(min_date)
                                col_data['max_date'] = str(max_date)
                except Exception as e:
                    col_data['error'] = str(e)
                
                column_insights[col_name] = col_data
            
            insights[table]['columns'] = column_insights
            
            # Additional table-specific analysis
            if table == 'payments':
                try:
                    # Split payments analysis
                    if safe_execute(cursor, "SELECT COUNT(DISTINCT split_group_id) FROM payments WHERE split_group_id IS NOT NULL"):
                        split_result = safe_fetch_one(cursor, [0])
                        split_groups = safe_get(split_result, 0, 0)
                        insights[table]['split_groups'] = split_groups
                    
                    # Analyze payment method distribution
                    if safe_execute(cursor, "SELECT method, COUNT(*) FROM payments WHERE method IS NOT NULL GROUP BY method ORDER BY COUNT(*) DESC"):
                        method_results = safe_fetch_all(cursor, [])
                        methods = {str(safe_get(row, 0, "")): safe_get(row, 1, 0) for row in method_results if row is not None}
                        insights[table]['methods'] = methods
                except Exception as e:
                    print(f"Error analyzing payments table: {e}")
                    insights[table]['error'] = str(e)
            
            elif table == 'contracts':
                try:
                    # Provider distribution
                    if safe_execute(cursor, "SELECT provider_name, COUNT(*) FROM contracts WHERE provider_name IS NOT NULL GROUP BY provider_name ORDER BY COUNT(*) DESC"):
                        provider_results = safe_fetch_all(cursor, [])
                        providers = {str(safe_get(row, 0, "")): safe_get(row, 1, 0) for row in provider_results if row is not None}
                        insights[table]['providers'] = providers
                    
                    # Payment schedule distribution
                    if safe_execute(cursor, "SELECT payment_schedule, COUNT(*) FROM contracts WHERE payment_schedule IS NOT NULL GROUP BY payment_schedule"):
                        schedule_results = safe_fetch_all(cursor, [])
                        schedules = {str(safe_get(row, 0, "")): safe_get(row, 1, 0) for row in schedule_results if row is not None}
                        insights[table]['payment_schedules'] = schedules
                    
                    # Fee type distribution
                    if safe_execute(cursor, "SELECT fee_type, COUNT(*) FROM contracts WHERE fee_type IS NOT NULL GROUP BY fee_type"):
                        fee_results = safe_fetch_all(cursor, [])
                        fee_types = {str(safe_get(row, 0, "")): safe_get(row, 1, 0) for row in fee_results if row is not None}
                        insights[table]['fee_types'] = fee_types
                except Exception as e:
                    print(f"Error analyzing contracts table: {e}")
                    insights[table]['error'] = str(e)
            
            elif table == 'clients':
                try:
                    # OneDrive path presence
                    if safe_execute(cursor, "SELECT COUNT(*) FROM clients WHERE onedrive_folder_path IS NOT NULL"):
                        path_result = safe_fetch_one(cursor, [0])
                        has_path = safe_get(path_result, 0, 0)
                        insights[table]['has_onedrive_path'] = has_path
                except Exception as e:
                    print(f"Error analyzing clients table: {e}")
                    insights[table]['error'] = str(e)
                    
            elif table == 'client_files':
                try:
                    # File extension analysis
                    # SQLite doesn't have a direct function to get the last part after the final dot
                    # Use a workaround by getting the entire filename and process it later
                    ext_query = """
                        SELECT 
                            file_name,
                            COUNT(*) as count
                        FROM client_files
                        WHERE file_name LIKE '%.%'
                        GROUP BY SUBSTR(file_name, INSTR(file_name, '.') + 1)
                        ORDER BY count DESC
                    """
                    if safe_execute(cursor, ext_query):
                        ext_results = safe_fetch_all(cursor, [])
                        # Process filenames to extract extensions
                        extensions = {}
                        for row in ext_results:
                            if row is None:
                                continue
                            filename = str(safe_get(row, 0, ""))
                            count = safe_get(row, 1, 0)
                            # Extract extension (everything after the last dot)
                            if '.' in filename:
                                ext = filename.split('.')[-1].lower()
                                if ext in extensions:
                                    extensions[ext] += count
                                else:
                                    extensions[ext] = count
                        insights[table]['extensions'] = extensions
                except Exception as e:
                    print(f"Error analyzing client_files table: {e}")
                    insights[table]['error'] = str(e)
            
            elif table == 'contacts':
                try:
                    # Contact type distribution
                    if safe_execute(cursor, "SELECT contact_type, COUNT(*) FROM contacts WHERE contact_type IS NOT NULL GROUP BY contact_type ORDER BY COUNT(*) DESC"):
                        type_results = safe_fetch_all(cursor, [])
                        contact_types = {str(safe_get(row, 0, "")): safe_get(row, 1, 0) for row in type_results if row is not None}
                        insights[table]['contact_types'] = contact_types
                except Exception as e:
                    print(f"Error analyzing contacts table: {e}")
                    insights[table]['error'] = str(e)
        
        # Generate markdown
        md_content = "# DB Insights for 401(k) Payment Tracking System\n\n"
        
        # For each table
        for table, table_data in insights.items():
            md_content += f"## Table: {table}\n"
            
            # Basic table stats
            md_content += f"- **Row Count**: {table_data.get('row_count', 0)}\n"
            
            # Table-specific additional insights
            if table == 'payments' and 'methods' in table_data:
                method_list = list(table_data['methods'].keys())
                md_content += f"- **Payment Methods**: {method_list}\n"
            elif table == 'contracts':
                if 'payment_schedules' in table_data:
                    schedules = table_data['payment_schedules']
                    total = sum(schedules.values()) if schedules else 0
                    schedule_values = list(schedules.keys()) if schedules else []
                    schedule_percentages = [f"{safe_int(100 * v / total)}" for v in schedules.values()] if total > 0 else ["0"]
                    md_content += f"- **Payment Schedules**: {schedule_values} ({'/'.join(schedule_percentages)}% split)\n"
                
                if 'fee_types' in table_data:
                    fee_types = table_data['fee_types']
                    total = sum(fee_types.values()) if fee_types else 0
                    fee_type_values = list(fee_types.keys()) if fee_types else []
                    fee_percentages = [f"{safe_int(100 * v / total)}" for v in fee_types.values()] if total > 0 else ["0"]
                    md_content += f"- **Fee Types**: {fee_type_values} ({'/'.join(fee_percentages)}% split)\n"
                
                if 'providers' in table_data:
                    providers = list(table_data.get('providers', {}).items())[:5]
                    provider_names = [p[0] for p in providers] if providers else []
                    md_content += f"- **Top Providers**: {provider_names}\n"
            elif table == 'client_files' and 'extensions' in table_data:
                ext_list = list(table_data['extensions'].keys())[:5] if table_data.get('extensions') else []
                md_content += f"- **Common Extensions**: {ext_list}\n"
            elif table == 'contacts' and 'contact_types' in table_data:
                type_list = list(table_data.get('contact_types', {}).keys())
                md_content += f"- **Contact Types**: {type_list}\n"
            
            # Column insights
            md_content += "- **Column Analysis**:\n"
            if 'columns' in table_data:
                for col_name, col_data in table_data.get('columns', {}).items():
                    # Create a concise representation of the column
                    col_info = []
                    
                    # Type and nullability
                    type_str = col_data.get('type', 'UNKNOWN')
                    if col_data.get('nullable', True):
                        null_pct = col_data.get('null_percent', 0)
                        if null_pct and null_pct > 0:
                            type_str += f" ({null_pct}% NULL)"
                    else:
                        type_str += " NOT NULL"
                    
                    col_info.append(type_str)
                    
                    # Value ranges for numeric
                    if 'min' in col_data and 'max' in col_data:
                        # Format differently for different types of numbers
                        try:
                            if col_data.get('appears_percentage', False):
                                col_info.append(f"range: {col_data['min']}%-{col_data['max']}%")
                            elif col_data.get('appears_currency', False):
                                col_info.append(f"range: ${safe_int(col_data['min'])}-${safe_int(col_data['max'])}")
                            else:
                                col_info.append(f"range: {col_data['min']}-{col_data['max']}")
                        except Exception:
                            col_info.append(f"range: {col_data.get('min', '?')}-{col_data.get('max', '?')}")
                    
                    # Date format
                    if col_data.get('appears_date', False) and 'format' in col_data:
                        col_info.append(f"format: {col_data['format']}")
                    
                    # Special field types
                    if col_data.get('appears_boolean', False):
                        col_info.append("boolean-like")
                    if col_data.get('appears_email', False):
                        col_info.append("email")
                    if col_data.get('appears_phone', False):
                        col_info.append("phone")
                    
                    # Show all values for low-cardinality fields
                    if 'values' in col_data and len(col_data['values']) <= 10:
                        values_str = ", ".join(col_data['values'].keys())
                        col_info.append(f"values: [{values_str}]")
                    elif 'distinct_count' in col_data and col_data['distinct_count'] > 0:
                        col_info.append(f"unique values: {col_data['distinct_count']}")
                    
                    # Add to markdown
                    md_content += f"  - **{col_name}**: {' | '.join(col_info)}\n"
            
            md_content += "\n"
        
        # Add common edge cases
        md_content += "## Common Edge Cases\n"
        md_content += "- Empty total_assets when fee_type='Fixed'\n"
        md_content += "- Split payments spanning year boundaries\n"
        md_content += "- Clients with changed fee structures mid-year\n"
        md_content += "- Multi-quarter payments (Q2-Q4 together)\n"
        md_content += "- Backdated payments (received_date > 60 days after period end)\n"
        md_content += "- Files with same name in different client folders\n\n"
        
        # General guidelines
        md_content += "## General Guidelines\n"
        md_content += "- Always handle NULL in optional fields (total_assets, method, notes)\n"
        md_content += "- Convert dates with datetime.strptime/strftime using 'YYYY-MM-DD' format\n"
        md_content += "- Format currency with locale.currency() for display\n"
        md_content += "- Payment period calculations: Use supplied AUM*rate if available, otherwise last known AUM*rate\n"
        md_content += "- Store decimal values with Decimal() not float for financial calculations\n"
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write(md_content)
        
        conn.close()
        return f"Analysis complete. Results saved to {output_path}"
        
    except Exception as e:
        return f"Fatal error: {e}"

if __name__ == "__main__":
    db_path = r"C:\CODING\investment-dashboard\backend\db\401KDB.db"
    output_path = r"C:\CODING\investment-dashboard\backend\db\db_insights.md"
    
    try:
        result = analyze_database(db_path, output_path)
        print(result)
    except Exception as e:
        print(f"Error: {e}")
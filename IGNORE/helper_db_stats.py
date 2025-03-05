import sqlite3
import os
import random
import re
from datetime import datetime
from collections import Counter
import math

# Input and output paths
DB_FILE_PATH = r"C:\CODING\investment-dashboard\backend\db\401KDB.db"
OUTPUT_DIR = os.path.dirname(DB_FILE_PATH)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "database_helper_stats.txt")

def is_date(value):
    """Check if a value appears to be a date."""
    if value is None or value == '':
        return False
    
    value_str = str(value).strip()
    
    date_patterns = [
        r'^\d{4}-\d{2}-\d{2}$',                  # YYYY-MM-DD
        r'^\d{2}/\d{2}/\d{4}$',                  # MM/DD/YYYY
        r'^\d{2}-\d{2}-\d{4}$',                  # MM-DD-YYYY
        r'^\d{4}/\d{2}/\d{2}$',                  # YYYY/MM/DD
        r'^\d{2}\.\d{2}\.\d{4}$',                # DD.MM.YYYY
        r'^\d{4}\.\d{2}\.\d{2}$',                # YYYY.MM.DD
        r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', # ISO format with time
    ]
    
    for pattern in date_patterns:
        if re.match(pattern, value_str):
            try:
                formats = ['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%Y/%m/%d', 
                          '%d.%m.%Y', '%Y.%m.%d', '%Y-%m-%dT%H:%M:%S']
                
                for fmt in formats:
                    try:
                        datetime.strptime(value_str.split('.')[0], fmt)
                        return True
                    except ValueError:
                        continue
            except:
                pass
    return False

def format_date(value):
    """Format a date string consistently."""
    if value is None or value == '':
        return None
    
    value_str = str(value).strip()
    formats = ['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%Y/%m/%d', 
              '%d.%m.%Y', '%Y.%m.%d', '%Y-%m-%dT%H:%M:%S']
    
    for fmt in formats:
        try:
            dt = datetime.strptime(value_str.split('.')[0], fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    return value

def is_float(value):
    """Check if a value can be converted to float."""
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, str):
        value = value.replace(',', '').strip()
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            if value.endswith('%'):
                try:
                    float(value[:-1])
                    return True
                except (ValueError, TypeError):
                    return False
            return False
    return False

def is_integer(value):
    """Check if a value can be converted to integer."""
    if isinstance(value, int):
        return True
    if isinstance(value, float):
        return value.is_integer()
    if isinstance(value, str):
        value = value.replace(',', '').strip()
        try:
            int_val = float(value)
            return int_val.is_integer()
        except (ValueError, TypeError):
            return False
    return False

def is_boolean(value):
    """Check if a value appears to be boolean."""
    if isinstance(value, bool):
        return True
    if value in (0, 1, '0', '1', 'true', 'false', 'True', 'False', 'TRUE', 'FALSE', 'yes', 'no', 'Yes', 'No', 'YES', 'NO'):
        return True
    return False

def is_structured_data(values):
    """Determine if a column contains structured data (limited set of distinct values)."""
    if not values:
        return False, []
    
    non_null_values = [v for v in values if v is not None and str(v).strip() != '']
    if not non_null_values:
        return False, []
    
    value_counts = Counter(non_null_values)
    unique_values = list(value_counts.keys())
    unique_count = len(unique_values)
    total_count = len(non_null_values)
    
    if total_count < 100:
        threshold = 10
    else:
        threshold = min(50, max(10, int(math.log(total_count) * 5)))
    
    ratio_threshold = 0.1
    
    is_structured = unique_count <= threshold or (unique_count / total_count) <= ratio_threshold
    
    if is_structured:
        sorted_values = sorted(unique_values, 
                              key=lambda x: (-value_counts[x], str(x)))
        if len(sorted_values) > 20:
            sorted_values = sorted_values[:20] + ["..."]
        
        sorted_values = [str(v) for v in sorted_values]
        return True, sorted_values
    
    return False, []

def determine_field_type(values):
    """Determine the predominant data type of a field."""
    if not values:
        return "UNKNOWN"
    
    non_null_values = [v for v in values if v is not None and str(v).strip() != '']
    if not non_null_values:
        return "UNKNOWN"
    
    types = {
        "INTEGER": 0,
        "REAL": 0,
        "TEXT": 0,
        "DATE": 0,
        "BOOLEAN": 0
    }
    
    sample_values = non_null_values
    if len(sample_values) > 1000:
        random.seed(42)
        sample_values = random.sample(non_null_values, 1000)
    
    for value in sample_values:
        if is_boolean(value):
            types["BOOLEAN"] += 1
        elif is_integer(value):
            types["INTEGER"] += 1
        elif is_float(value):
            types["REAL"] += 1
        elif is_date(value):
            types["DATE"] += 1
        else:
            types["TEXT"] += 1
    
    predominant_type = max(types.items(), key=lambda x: x[1])[0]
    
    if predominant_type == "INTEGER" and types["REAL"] > 0:
        return "REAL"
    
    return predominant_type

def calculate_type_consistency(values, field_type):
    """Calculate the percentage of values that match the determined field type."""
    if not values:
        return 100.0
    
    non_null_values = [v for v in values if v is not None and str(v).strip() != '']
    if not non_null_values:
        return 100.0
    
    sample_values = non_null_values
    if len(sample_values) > 1000:
        random.seed(42)
        sample_values = random.sample(non_null_values, 1000)
    
    consistent_count = 0
    
    for value in sample_values:
        if field_type == "INTEGER" and is_integer(value):
            consistent_count += 1
        elif field_type == "REAL" and is_float(value):
            consistent_count += 1
        elif field_type == "DATE" and is_date(value):
            consistent_count += 1
        elif field_type == "BOOLEAN" and is_boolean(value):
            consistent_count += 1
        elif field_type == "TEXT":
            consistent_count += 1
    
    return (consistent_count / len(sample_values)) * 100.0

def check_foreign_key_integrity(conn, table_name, field_name):
    """Check if a field could be a foreign key and calculate match percentage."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        tables = [t for t in tables if not t.startswith('sqlite_')]
        
        cursor.execute(f"SELECT DISTINCT `{field_name}` FROM `{table_name}` WHERE `{field_name}` IS NOT NULL LIMIT 1000;")
        values = [row[0] for row in cursor.fetchall()]
        
        if not values:
            return None
        
        best_match = None
        best_match_pct = 0
        
        for ref_table in tables:
            if ref_table == table_name:
                continue
            
            cursor.execute(f"PRAGMA table_info(`{ref_table}`);")
            columns = cursor.fetchall()
            
            for col in columns:
                col_name = col[1]
                is_pk = col[5]
                
                if is_pk or col_name.lower() in ('id', f'{ref_table.lower()}_id', 'key', 'code'):
                    cursor.execute(f"SELECT DISTINCT `{col_name}` FROM `{ref_table}` LIMIT 1000;")
                    ref_values = set(row[0] for row in cursor.fetchall())
                    
                    if not ref_values:
                        continue
                    
                    matched = sum(1 for v in values if v in ref_values)
                    if not matched:
                        continue
                        
                    match_pct = (matched / len(values)) * 100
                    
                    if match_pct > best_match_pct and match_pct >= 80:
                        best_match = (ref_table, col_name, match_pct, 100 - match_pct)
                        best_match_pct = match_pct
        
        return best_match
    except:
        return None

def format_value(value):
    """Format a value for display in the sample data."""
    if value is None:
        return ""
    elif isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        else:
            return f"{value:.2f}"
    else:
        return str(value)

def calculate_duplicate_rows(conn, table_name, columns):
    """Calculate the number of duplicate rows in a table."""
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`;")
        row_count = cursor.fetchone()[0]
        
        if row_count > 100000:
            return 0
        
        column_list = ", ".join([f"`{col}`" for col in columns])
        
        try:
            cursor.execute(f"""
                SELECT COUNT(*) - COUNT(DISTINCT {column_list}) 
                FROM `{table_name}`;
            """)
            return cursor.fetchone()[0]
        except sqlite3.OperationalError:
            return 0
    except:
        return 0

def main():
    try:
        conn = sqlite3.connect(DB_FILE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        tables = [t for t in tables if not t.startswith('sqlite_')]
        
        output_lines = []
        
        for table_idx, table_name in enumerate(tables, 1):
            try:
                cursor.execute(f"PRAGMA table_info(`{table_name}`);")
                columns_info = cursor.fetchall()
                columns = [row[1] for row in columns_info]
                
                cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`;")
                total_rows = cursor.fetchone()[0]
                
                has_client_id = False
                client_id_field = None
                
                for col in columns:
                    if col.lower() == 'client_id':
                        has_client_id = True
                        client_id_field = col
                        break
                
                unique_client_ids = 0
                
                if has_client_id:
                    cursor.execute(f"SELECT COUNT(DISTINCT `{client_id_field}`) FROM `{table_name}`;")
                    unique_client_ids = cursor.fetchone()[0]
                
                duplicate_rows = calculate_duplicate_rows(conn, table_name, columns)
                
                output_lines.append(f"{table_idx}. TABLE: {table_name}")
                output_lines.append(f"- Total Rows: {total_rows}")
                if has_client_id:
                    output_lines.append(f"- Unique client_ids: {unique_client_ids}")
                output_lines.append(f"- Duplicate Rows: {duplicate_rows}")
                output_lines.append("")
                
                output_lines.append(f"{table_name} SAMPLE DATA:")
                
                header_row = " | ".join(columns)
                output_lines.append(header_row)
                
                for i in range(3):
                    if total_rows <= 5:
                        cursor.execute(f"SELECT * FROM `{table_name}`;")
                    else:
                        random_start = random.randint(0, max(0, total_rows - 5))
                        cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 5 OFFSET {random_start};")
                    
                    rows = cursor.fetchall()
                    for row in rows:
                        formatted_values = []
                        for j, col in enumerate(columns):
                            formatted_values.append(format_value(row[j]))
                        output_lines.append(" | ".join(formatted_values))
                    
                    if i < 2 and total_rows > 5:
                        output_lines.append("...")
                
                output_lines.append("")
                
                for field_idx, field_name in enumerate(columns, 1):
                    try:
                        cursor.execute(f"SELECT `{field_name}` FROM `{table_name}` LIMIT 5000;")
                        values = [row[0] for row in cursor.fetchall()]
                        
                        field_type = determine_field_type(values)
                        
                        output_lines.append(f"{table_idx}.{field_idx} FIELD: {field_name}")
                        output_lines.append(f"- Type: {field_type}")
                        
                        if field_type == "TEXT":
                            non_null_values = [str(v) for v in values if v is not None and str(v).strip() != '']
                            if non_null_values:
                                avg_length = sum(len(str(v)) for v in non_null_values) / len(non_null_values)
                                output_lines.append(f"- Avg Length (text fields only): {avg_length:.1f}")
                        
                        if field_type == "DATE":
                            date_values = [format_date(v) for v in values if v is not None and is_date(v)]
                            if date_values:
                                date_values.sort()
                                output_lines.append(f"- Date Range (date fields only): {date_values[0]} to {date_values[-1]}")
                        
                        consistency = calculate_type_consistency(values, field_type)
                        output_lines.append(f"- Type Consistency (excl. NULLs): {consistency:.1f}%")
                        
                        null_count = sum(1 for v in values if v is None or str(v).strip() == '')
                        null_percent = (null_count / len(values)) * 100 if values else 0
                        output_lines.append(f"- NULL Count: {null_count} ({null_percent:.1f}%)")
                        
                        non_null_values = [v for v in values if v is not None and str(v).strip() != '']
                        unique_values = set(str(v) for v in non_null_values)
                        cardinality = (len(unique_values) / len(non_null_values)) * 100 if non_null_values else 0
                        output_lines.append(f"- Cardinality: {cardinality:.1f}%")
                        
                        is_structured, structured_values = is_structured_data(values)
                        output_lines.append(f"- Structured Data: {'YES' if is_structured else 'NO'}")
                        if is_structured:
                            output_lines.append(f"- If Structured, options: {', '.join(structured_values)}")
                        
                        if field_type in ["INTEGER", "TEXT"] and cardinality < 50:
                            fk_info = check_foreign_key_integrity(conn, table_name, field_name)
                            if fk_info:
                                ref_table, ref_col, match_pct, unmatch_pct = fk_info
                                output_lines.append(f"- Foreign Key Integrity (if applicable): matched {match_pct:.1f}%, unmatched {unmatch_pct:.1f}%")
                        
                        output_lines.append("")
                    except Exception as e:
                        output_lines.append(f"{table_idx}.{field_idx} FIELD: {field_name}")
                        output_lines.append(f"- Error analyzing field: {str(e)}")
                        output_lines.append("")
                
                if table_idx < len(tables):
                    output_lines.append("---")
                    output_lines.append("")
            
            except Exception as e:
                output_lines.append(f"{table_idx}. TABLE: {table_name}")
                output_lines.append(f"- Error analyzing table: {str(e)}")
                output_lines.append("")
                if table_idx < len(tables):
                    output_lines.append("---")
                    output_lines.append("")
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        
        conn.close()
        print(f"Database stats written to {OUTPUT_FILE}")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
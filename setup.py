import os
import subprocess
import mysql.connector
from mysql.connector import errorcode

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '3149550729_AnF',
}

DB_NAME = 'course_selection_system'

def create_database():
    """Create the database and initialize schema"""
    conn = None
    try:
        # Connect to MySQL server
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        print(f"Creating database {DB_NAME}...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"Database {DB_NAME} created (or already exists).")
        
        # Use the database
        cursor.execute(f"USE {DB_NAME}")
        
        # Read and execute SQL file
        with open('schema.sql', 'r', encoding='utf-8') as f:
            sql_commands = f.read()
        
        # Split SQL commands by semicolon
        for command in sql_commands.split(';'):
            if command.strip():
                try:
                    cursor.execute(command)
                    conn.commit()
                except mysql.connector.Error as err:
                    print(f"Error executing command: {err}")
                    print(f"Command: {command}")
        
        print("Database schema created successfully.")
    
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error: Access denied. Check username and password.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print(f"Error: Database {DB_NAME} does not exist.")
        else:
            print(f"Error: {err}")
    finally:
        if conn is not None and conn.is_connected():
            cursor.close()
            conn.close()
            print("Database connection closed.")

def create_triggers():
    """Create triggers separately since DELIMITER syntax needs special handling"""
    try:
        # Connect to MySQL server
        config = DB_CONFIG.copy()
        config['database'] = DB_NAME
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        print("Creating triggers...")
        
        # Create insert trigger
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_score_record_before_insert
        BEFORE INSERT ON score_record
        FOR EACH ROW
        BEGIN
            IF NEW.usual_score IS NOT NULL AND NEW.final_score IS NOT NULL THEN
                SET NEW.total_score = NEW.usual_score * 0.4 + NEW.final_score * 0.6;
            END IF;
        END
        """)
        
        # Create update trigger
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_score_record_before_update
        BEFORE UPDATE ON score_record
        FOR EACH ROW
        BEGIN
            IF NEW.usual_score IS NOT NULL AND NEW.final_score IS NOT NULL THEN
                SET NEW.total_score = NEW.usual_score * 0.4 + NEW.final_score * 0.6;
            END IF;
        END
        """)
        
        conn.commit()
        print("Triggers created successfully.")
        
    except mysql.connector.Error as err:
        print(f"Error creating triggers: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def initialize_test_data():
    """Initialize test data in the database"""
    print("Initializing test data...")
    try:
        # Run the init_data.py script directly
        import init_data
        init_data.init_test_data()
        print("Test data initialized successfully.")
    except Exception as e:
        print(f"Error initializing test data: {e}")

def setup_stored_procedures():
    """Initialize stored procedures"""
    print("Setting up stored procedures...")
    try:
        # Use direct database connection to create procedures
        config = DB_CONFIG.copy()
        config['database'] = DB_NAME
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # Drop procedure if exists
        cursor.execute("DROP PROCEDURE IF EXISTS CalculateFinalGrades")
        
        # Create stored procedure for calculating final grades
        cursor.execute("""
        CREATE PROCEDURE CalculateFinalGrades(IN p_course_id CHAR(8), IN p_semester VARCHAR(20))
        BEGIN
            UPDATE score_record sr
            JOIN course_selection cs ON sr.course_selection_id = cs.id
            SET sr.total_score = sr.usual_score * 0.4 + sr.final_score * 0.6
            WHERE cs.course_id = p_course_id AND cs.semester = p_semester;
            
            SELECT s.student_id, s.name, sr.usual_score, sr.final_score, sr.total_score
            FROM course_selection cs
            JOIN student s ON cs.student_id = s.student_id
            JOIN score_record sr ON cs.id = sr.course_selection_id
            WHERE cs.course_id = p_course_id AND cs.semester = p_semester;
        END
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Stored procedures created successfully.")
    except Exception as e:
        print(f"Error setting up stored procedures: {e}")

def start_server():
    """Start the Flask server"""
    print("Starting Flask server...")
    try:
        # Run the main.py script
        subprocess.run(['python', 'main.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
    except KeyboardInterrupt:
        print("Server stopped.")

def extract_schema_from_sql():
    """Extract schema from CreateTable.sql file"""
    try:
        # Read the original SQL file
        with open('../dbSetting/CreateTable.sql', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the boundaries for the schema (tables and indexes)
        start_index = content.find("CREATE TABLE login_info")
        end_index = content.find("# 课内事务")
        
        if start_index >= 0 and end_index >= 0:
            schema_sql = content[start_index:end_index]
            
            # Write to schema.sql file
            with open('schema.sql', 'w', encoding='utf-8') as f:
                f.write(schema_sql)
            
            print("Schema extracted successfully.")
        else:
            print("Could not find schema boundaries in SQL file.")
            # Create a simple schema from scratch if extraction fails
            create_basic_schema()
    
    except Exception as e:
        print(f"Error extracting schema: {e}")
        # Create a simple schema from scratch if extraction fails
        create_basic_schema()

def create_basic_schema():
    """Create a basic schema file if extraction fails"""
    print("Creating basic schema file...")
    schema_content = """
-- User Authentication
CREATE TABLE IF NOT EXISTS login_info (
    user_id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'teacher', 'student') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    UNIQUE (username)
) AUTO_INCREMENT = 100000000;

-- Department
CREATE TABLE IF NOT EXISTS department (
    dept_id CHAR(2) NOT NULL,
    dept_name VARCHAR(100) NOT NULL,
    address VARCHAR(255),
    phone_code VARCHAR(15),
    PRIMARY KEY (dept_id)
);

-- Student
CREATE TABLE IF NOT EXISTS student (
    student_id CHAR(8) NOT NULL,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    sex ENUM('M', 'F') NOT NULL,
    date_of_birth DATE NOT NULL,
    native_place VARCHAR(100),
    mobile_phone VARCHAR(15),
    dept_id CHAR(2) NOT NULL,
    status ENUM('active', 'inactive') NOT NULL,
    PRIMARY KEY (student_id),
    FOREIGN KEY (user_id) REFERENCES login_info(user_id),
    FOREIGN KEY (dept_id) REFERENCES department(dept_id)
);

-- Teacher
CREATE TABLE IF NOT EXISTS teacher (
    staff_id CHAR(8) NOT NULL,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    sex ENUM('M', 'F') NOT NULL,
    date_of_birth DATE NOT NULL,
    professional_ranks VARCHAR(100),
    salary DECIMAL(10, 2),
    dept_id CHAR(2) NOT NULL,
    PRIMARY KEY (staff_id),
    FOREIGN KEY (user_id) REFERENCES login_info(user_id),
    FOREIGN KEY (dept_id) REFERENCES department(dept_id)
);

-- Course
CREATE TABLE IF NOT EXISTS course (
    course_id CHAR(8) NOT NULL,
    course_name VARCHAR(100) NOT NULL,
    credit INT DEFAULT 4,
    credit_hours INT DEFAULT 40,
    dept_id CHAR(2) NOT NULL,
    PRIMARY KEY (course_id),
    FOREIGN KEY (dept_id) REFERENCES department(dept_id)
);

-- Class offerings
CREATE TABLE IF NOT EXISTS class (
    semester VARCHAR(20) NOT NULL,
    course_id CHAR(8) NOT NULL,
    staff_id CHAR(8) NOT NULL,
    class_time DATETIME NOT NULL,
    PRIMARY KEY (semester, course_id, staff_id),
    FOREIGN KEY (course_id) REFERENCES course(course_id),
    FOREIGN KEY (staff_id) REFERENCES teacher(staff_id)
);

-- Course selection
CREATE TABLE IF NOT EXISTS course_selection (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id CHAR(8) NOT NULL,
    semester VARCHAR(20) NOT NULL,
    course_id CHAR(8) NOT NULL,
    staff_id CHAR(8) NOT NULL,
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    FOREIGN KEY (course_id) REFERENCES course(course_id),
    FOREIGN KEY (staff_id) REFERENCES teacher(staff_id),
    UNIQUE (student_id, semester, course_id)
);

-- Score records
CREATE TABLE IF NOT EXISTS score_record (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_selection_id INT NOT NULL UNIQUE,
    usual_score DECIMAL(5,2),
    final_score DECIMAL(5,2),
    total_score DECIMAL(5,2),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (course_selection_id) REFERENCES course_selection(id)
);

-- Admin
CREATE TABLE IF NOT EXISTS admin (
    admin_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    role ENUM('superadmin', 'admin') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (admin_id),
    FOREIGN KEY (user_id) REFERENCES login_info(user_id)
);
    """
    
    with open('schema.sql', 'w', encoding='utf-8') as f:
        f.write(schema_content)
    
    print("Basic schema file created.")

if __name__ == "__main__":
    # Extract or create schema
    extract_schema_from_sql()
    
    # Create database and schema
    create_database()
    
    # Create triggers separately
    create_triggers()
    
    # Create stored procedures
    setup_stored_procedures()
    
    # Initialize test data
    initialize_test_data()
    
    # Start server
    start_server() 
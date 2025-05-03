import mysql.connector
from datetime import datetime

# Database connection parameters
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '3149550729_AnF',
    'database': 'course_selection_system'
}

def init_test_data():
    try:
        # Connect to database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Add departments
        departments = [
            ('01', 'Computer Science', 'Building A', '123-456-7890'),
            ('02', 'Mathematics', 'Building B', '123-456-7891'),
            ('03', 'Physics', 'Building C', '123-456-7892'),
            ('04', 'Chemistry', 'Building D', '123-456-7893')
        ]
        
        cursor.executemany(
            "INSERT INTO department (dept_id, dept_name, address, phone_code) VALUES (%s, %s, %s, %s)",
            departments
        )
        
        # Add user accounts
        users = [
            # Admin
            (100000001, 'admin', 'admin123', 'admin'),
            # Teachers
            (100000002, 'teacher1', 'password', 'teacher'),
            (100000003, 'teacher2', 'password', 'teacher'),
            (100000004, 'teacher3', 'password', 'teacher'),
            # Students
            (100000005, 'student1', 'password', 'student'),
            (100000006, 'student2', 'password', 'student'),
            (100000007, 'student3', 'password', 'student')
        ]
        
        cursor.executemany(
            "INSERT INTO login_info (user_id, username, password, role) VALUES (%s, %s, %s, %s)",
            users
        )
        
        # Add admin account
        cursor.execute(
            "INSERT INTO admin (admin_id, user_id, role) VALUES (%s, %s, %s)",
            (1, 100000001, 'admin')
        )
        
        # Add teachers
        teachers = [
            ('10000001', 100000002, 'John Smith', 'M', '1980-01-15', 'Professor', 80000.00, '01'),
            ('10000002', 100000003, 'Mary Johnson', 'F', '1975-05-23', 'Associate Professor', 70000.00, '02'),
            ('10000003', 100000004, 'David Lee', 'M', '1982-11-08', 'Assistant Professor', 60000.00, '03')
        ]
        
        cursor.executemany(
            "INSERT INTO teacher (staff_id, user_id, name, sex, date_of_birth, professional_ranks, salary, dept_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            teachers
        )
        
        # Add students
        students = [
            ('20230001', 100000005, 'Alice Brown', 'F', '2000-03-10', 'New York', '555-123-4567', '01', 'active'),
            ('20230002', 100000006, 'Bob Wilson', 'M', '2001-07-22', 'Chicago', '555-234-5678', '02', 'active'),
            ('20230003', 100000007, 'Carol Martinez', 'F', '2001-12-05', 'Los Angeles', '555-345-6789', '03', 'active')
        ]
        
        cursor.executemany(
            "INSERT INTO student (student_id, user_id, name, sex, date_of_birth, native_place, mobile_phone, dept_id, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            students
        )
        
        # Add courses
        courses = [
            ('CS101', 'Introduction to Programming', 4, 40, '01'),
            ('CS201', 'Data Structures', 4, 40, '01'),
            ('MATH101', 'Calculus I', 4, 40, '02'),
            ('MATH201', 'Linear Algebra', 3, 30, '02'),
            ('PHYS101', 'Physics I', 4, 40, '03'),
            ('CHEM101', 'Chemistry I', 4, 40, '04')
        ]
        
        cursor.executemany(
            "INSERT INTO course (course_id, course_name, credit, credit_hours, dept_id) VALUES (%s, %s, %s, %s, %s)",
            courses
        )
        
        # Add class offerings
        classes = [
            ('2023-2024-1', 'CS101', '10000001', '2023-09-01 09:00:00'),
            ('2023-2024-1', 'MATH101', '10000002', '2023-09-01 13:00:00'),
            ('2023-2024-1', 'PHYS101', '10000003', '2023-09-02 09:00:00'),
            ('2023-2024-2', 'CS201', '10000001', '2024-02-01 09:00:00'),
            ('2023-2024-2', 'MATH201', '10000002', '2024-02-01 13:00:00'),
            ('2023-2024-2', 'CHEM101', '10000003', '2024-02-02 09:00:00')
        ]
        
        cursor.executemany(
            "INSERT INTO class (semester, course_id, staff_id, class_time) VALUES (%s, %s, %s, %s)",
            classes
        )
        
        # Add some course selections
        selections = [
            ('20230001', '2023-2024-1', 'CS101', '10000001'),
            ('20230001', '2023-2024-1', 'MATH101', '10000002'),
            ('20230002', '2023-2024-1', 'MATH101', '10000002'),
            ('20230002', '2023-2024-1', 'PHYS101', '10000003'),
            ('20230003', '2023-2024-1', 'CS101', '10000001'),
            ('20230003', '2023-2024-1', 'PHYS101', '10000003')
        ]
        
        cursor.executemany(
            "INSERT INTO course_selection (student_id, semester, course_id, staff_id) VALUES (%s, %s, %s, %s)",
            selections
        )
        
        # Get course_selection IDs for adding scores
        cursor.execute("SELECT id, student_id, course_id FROM course_selection WHERE semester = '2023-2024-1'")
        selection_results = cursor.fetchall()
        
        # Add some scores
        for selection_id, student_id, course_id in selection_results:
            # Generate some random-ish scores based on student and course
            usual_score = 70 + (int(student_id[-1]) * int(course_id[-1])) % 30
            final_score = 65 + (int(student_id[-1]) * int(course_id[-1])) % 35
            
            cursor.execute(
                "INSERT INTO score_record (course_selection_id, usual_score, final_score) VALUES (%s, %s, %s)",
                (selection_id, usual_score, final_score)
            )
        
        # Commit changes
        conn.commit()
        print("Test data initialized successfully!")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        conn.rollback()
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    init_test_data() 
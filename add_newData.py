import mysql.connector
from datetime import datetime, timedelta
import random

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '3149550729_AnF',
    'database': 'course_selection_system'
}

def add_future_test_data():
    """添加2025-2026学期及其他新测试数据"""
    try:
        # 连接数据库
        print("连接数据库...")
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 添加新学期
        future_semesters = [
            ('2025-2026-1', False),  # 2025-2026学年第一学期
            ('2025-2026-2', False)   # 2025-2026学年第二学期
        ]
        
        print("添加未来学期...")
        for semester in future_semesters:
            # 检查学期是否已存在
            cursor.execute("SELECT 1 FROM semester WHERE semester_id = %s", [semester[0]])
            if cursor.fetchone():
                print(f"学期 {semester[0]} 已存在，跳过")
                continue
                
            cursor.execute('''
                INSERT INTO semester (semester_id, is_current)
                VALUES (%s, %s)
            ''', semester)
            print(f"学期 {semester[0]} 已添加")
        
        # 为2025-2026-1学期添加课程安排
        print("为2025-2026-1学期添加课程安排...")
        future_classes_1 = [
            ('2025-2026-1', 'CS101', 'T1000001', '2025-09-01 08:00:00'),
            ('2025-2026-1', 'CS102', 'T1000002', '2025-09-01 10:00:00'),
            ('2025-2026-1', 'CS103', 'T1000001', '2025-09-02 08:00:00'),
            ('2025-2026-1', 'CS104', 'T1000002', '2025-09-02 10:00:00'),
            ('2025-2026-1', 'EE101', 'T1000003', '2025-09-03 08:00:00'),
            ('2025-2026-1', 'MA101', 'T1000004', '2025-09-04 08:00:00'),
            ('2025-2026-1', 'PH101', 'T1000005', '2025-09-05 08:00:00')
        ]
        
        # 为2025-2026-2学期添加课程安排
        print("为2025-2026-2学期添加课程安排...")
        future_classes_2 = [
            ('2025-2026-2', 'CS102', 'T1000001', '2026-02-01 08:00:00'),
            ('2025-2026-2', 'CS103', 'T1000002', '2026-02-01 10:00:00'),
            ('2025-2026-2', 'CS104', 'T1000001', '2026-02-02 08:00:00'),
            ('2025-2026-2', 'CS105', 'T1000002', '2026-02-02 10:00:00'),
            ('2025-2026-2', 'EE102', 'T1000003', '2026-02-03 08:00:00'),
            ('2025-2026-2', 'MA102', 'T1000004', '2026-02-04 08:00:00'),
            ('2025-2026-2', 'CH101', 'T1000005', '2026-02-05 08:00:00')
        ]
        
        future_classes = future_classes_1 + future_classes_2
        
        for class_info in future_classes:
            # 检查该课程安排是否已存在
            cursor.execute('''
                SELECT 1 FROM class 
                WHERE semester = %s AND course_id = %s AND staff_id = %s
            ''', (class_info[0], class_info[1], class_info[2]))
            
            if cursor.fetchone():
                print(f"课程安排已存在: {class_info[0]} - {class_info[1]} - {class_info[2]}")
                continue
                
            cursor.execute('''
                INSERT INTO class (semester, course_id, staff_id, class_time)
                VALUES (%s, %s, %s, %s)
            ''', class_info)
            print(f"添加课程安排: {class_info[0]} - {class_info[1]} - {class_info[2]}")
        
        # 添加新的学生
        print("添加新学生...")
        new_students = [
            (None, 'student11', 'student123', 'student'),
            (None, 'student12', 'student123', 'student'),
            (None, 'student13', 'student123', 'student'),
            (None, 'student14', 'student123', 'student'),
            (None, 'student15', 'student123', 'student')
        ]
        
        new_student_ids = []
        for student in new_students:
            # 检查用户名是否已存在
            cursor.execute("SELECT 1 FROM login_info WHERE username = %s", [student[1]])
            if cursor.fetchone():
                print(f"用户名 {student[1]} 已存在，跳过")
                continue
                
            cursor.execute('''
                INSERT INTO login_info (user_id, username, password, role)
                VALUES (%s, %s, %s, %s)
            ''', student)
            
            user_id = cursor.lastrowid
            new_student_ids.append((user_id, student[1]))
            print(f"添加新学生账号: {student[1]}, ID: {user_id}")
        
        # 为新学生添加学生信息
        for idx, (user_id, username) in enumerate(new_student_ids):
            student_id = f'S2025{idx+1:03}'
            name = f'新生{idx+1}'
            dept_id = f'0{(idx % 5) + 1}'  # 分配到不同院系
            
            cursor.execute('''
                INSERT INTO student (student_id, user_id, name, sex, date_of_birth, native_place, mobile_phone, dept_id, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (student_id, user_id, name, 'M' if idx % 2 == 0 else 'F', 
                  '2003-01-01', '北京', f'1381234{56+idx:02}', dept_id, 'active'))
            print(f"添加学生信息: {student_id} - {name} - {dept_id}")
        
        # 添加新教师
        print("添加新教师...")
        new_teachers = [
            (None, 'teacher6', 'teacher123', 'teacher'),
            (None, 'teacher7', 'teacher123', 'teacher')
        ]
        
        new_teacher_ids = []
        for teacher in new_teachers:
            # 检查用户名是否已存在
            cursor.execute("SELECT 1 FROM login_info WHERE username = %s", [teacher[1]])
            if cursor.fetchone():
                print(f"用户名 {teacher[1]} 已存在，跳过")
                continue
                
            cursor.execute('''
                INSERT INTO login_info (user_id, username, password, role)
                VALUES (%s, %s, %s, %s)
            ''', teacher)
            
            user_id = cursor.lastrowid
            new_teacher_ids.append((user_id, teacher[1]))
            print(f"添加新教师账号: {teacher[1]}, ID: {user_id}")
        
        # 为新教师添加教师信息
        for idx, (user_id, username) in enumerate(new_teacher_ids):
            staff_id = f'T1000{6+idx:03}'
            name = f'新教授{idx+1}'
            dept_id = f'0{(idx % 5) + 1}'  # 分配到不同院系
            
            cursor.execute('''
                INSERT INTO teacher (staff_id, user_id, name, sex, date_of_birth, professional_ranks, salary, dept_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (staff_id, user_id, name, 'M', '1985-01-01', 
                  '副教授', 10000.00, dept_id))
            print(f"添加教师信息: {staff_id} - {name} - {dept_id}")
        
        # 添加新课程
        print("添加新课程...")
        new_courses = [
            ('CS201', '高级程序设计', 4, 48, '01'),
            ('CS202', '人工智能导论', 3, 40, '01'),
            ('EE201', '数字信号处理', 4, 48, '02'),
            ('MA201', '复变函数', 4, 48, '03')
        ]
        
        for course in new_courses:
            # 检查课程是否已存在
            cursor.execute("SELECT 1 FROM course WHERE course_id = %s", [course[0]])
            if cursor.fetchone():
                print(f"课程 {course[0]} 已存在，跳过")
                continue
                
            cursor.execute('''
                INSERT INTO course (course_id, course_name, credit, credit_hours, dept_id)
                VALUES (%s, %s, %s, %s, %s)
            ''', course)
            print(f"添加新课程: {course[0]} - {course[1]}")
        
        # 为这些新课程创建2025-2026学年的课程安排
        print("为新课程创建未来学期的课程安排...")
        new_course_arrangements = [
            ('2025-2026-1', 'CS201', 'T1000001', '2025-09-06 08:00:00'),
            ('2025-2026-1', 'CS202', 'T1000002', '2025-09-06 10:00:00'),
            ('2025-2026-1', 'EE201', 'T1000003', '2025-09-07 08:00:00'),
            ('2025-2026-1', 'MA201', 'T1000004', '2025-09-07 10:00:00'),
            ('2025-2026-2', 'CS201', 'T1000006', '2026-02-06 08:00:00'),
            ('2025-2026-2', 'CS202', 'T1000007', '2026-02-06 10:00:00')
        ]
        
        for arrangement in new_course_arrangements:
            # 检查该课程安排是否已存在
            cursor.execute('''
                SELECT 1 FROM class 
                WHERE semester = %s AND course_id = %s AND staff_id = %s
            ''', (arrangement[0], arrangement[1], arrangement[2]))
            
            if cursor.fetchone():
                print(f"课程安排已存在: {arrangement[0]} - {arrangement[1]} - {arrangement[2]}")
                continue
                
            cursor.execute('''
                INSERT INTO class (semester, course_id, staff_id, class_time)
                VALUES (%s, %s, %s, %s)
            ''', arrangement)
            print(f"添加课程安排: {arrangement[0]} - {arrangement[1]} - {arrangement[2]}")
        
        # 添加一些虚拟选课记录（为老学生选择未来课程）
        print("添加未来选课记录...")
        # 获取所有学生ID
        cursor.execute("SELECT student_id FROM student")
        student_ids = [row[0] for row in cursor.fetchall()]
        
        for student_id in student_ids:
            # 为每个学生选择2025-2026-1学期的2-4门课
            num_courses = random.randint(2, 4)
            available_courses = list(future_classes_1)
            random.shuffle(available_courses)
            
            for i in range(min(num_courses, len(available_courses))):
                class_info = available_courses[i]
                
                # 检查该选课记录是否已存在
                cursor.execute('''
                    SELECT 1 FROM course_selection 
                    WHERE student_id = %s AND semester = %s AND course_id = %s
                ''', (student_id, class_info[0], class_info[1]))
                
                if cursor.fetchone():
                    print(f"选课记录已存在: {student_id} - {class_info[0]} - {class_info[1]}")
                    continue
                    
                cursor.execute('''
                    INSERT INTO course_selection (student_id, semester, course_id, staff_id)
                    VALUES (%s, %s, %s, %s)
                ''', (student_id, class_info[0], class_info[1], class_info[2]))
                print(f"添加选课记录: {student_id} - {class_info[0]} - {class_info[1]}")
        
        # 提交所有更改
        conn.commit()
        print("未来学期和测试数据添加完成！")
        
    except mysql.connector.Error as err:
        print(f"错误: {err}")
        conn.rollback()
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("数据库连接已关闭。")

if __name__ == "__main__":
    add_future_test_data() 
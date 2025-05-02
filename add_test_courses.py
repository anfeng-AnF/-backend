import mysql.connector
from datetime import datetime

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'course_selection_system'
}

def add_test_data():
    """向数据库添加测试数据，包括院系、课程、教师和班级信息"""
    try:
        # 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 获取当前学期
        current_year = datetime.now().year
        current_month = datetime.now().month
        semester = f"{current_year}-{current_year+1}-{1 if current_month < 8 else 2}"
        
        print(f"添加 {semester} 学期测试数据...")
        
        # 1. 添加院系数据
        departments = [
            ('01', '计算机科学与技术学院', '主楼A区', '12345678'),
            ('02', '电子信息工程学院', '主楼B区', '23456789'),
            ('03', '数学学院', '理科楼', '34567890'),
            ('04', '物理学院', '理科楼', '45678901'),
            ('05', '外国语学院', '文科楼', '56789012')
        ]
        
        for dept in departments:
            try:
                cursor.execute("""
                    INSERT INTO department (dept_id, dept_name, address, phone_code)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE dept_name=VALUES(dept_name), address=VALUES(address), phone_code=VALUES(phone_code)
                """, dept)
                conn.commit()
            except mysql.connector.Error as err:
                print(f"添加院系失败: {err}")
        
        # 2. 添加管理员账户
        try:
            cursor.execute("""
                INSERT INTO login_info (username, password, role)
                VALUES ('admin', 'admin123', 'admin')
                ON DUPLICATE KEY UPDATE password='admin123'
            """)
            admin_id = cursor.lastrowid
            
            # 检查是否已存在admin账户，如果是，获取其ID
            if not admin_id:
                cursor.execute("SELECT user_id FROM login_info WHERE username='admin'")
                admin_id = cursor.fetchone()[0]
                
            # 添加到admin表
            cursor.execute("""
                INSERT INTO admin (user_id, role)
                VALUES (%s, 'admin')
                ON DUPLICATE KEY UPDATE role='admin'
            """, (admin_id,))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"添加管理员账户失败: {err}")
        
        # 3. 添加教师账户和信息
        teachers = [
            ('teacher1', 'teacher123', 'T10001', '张教授', 'M', '1980-01-01', '教授', 80000, '01'),
            ('teacher2', 'teacher123', 'T10002', '李副教授', 'F', '1985-02-15', '副教授', 60000, '01'),
            ('teacher3', 'teacher123', 'T10003', '王讲师', 'M', '1990-05-20', '讲师', 40000, '02'),
            ('teacher4', 'teacher123', 'T10004', '赵教授', 'F', '1978-12-10', '教授', 85000, '03'),
            ('teacher5', 'teacher123', 'T10005', '刘副教授', 'M', '1982-07-05', '副教授', 62000, '04')
        ]
        
        for teacher in teachers:
            try:
                # 添加登录信息
                cursor.execute("""
                    INSERT INTO login_info (username, password, role)
                    VALUES (%s, %s, 'teacher')
                    ON DUPLICATE KEY UPDATE password=%s
                """, (teacher[0], teacher[1], teacher[1]))
                
                teacher_user_id = cursor.lastrowid
                if not teacher_user_id:
                    cursor.execute("SELECT user_id FROM login_info WHERE username=%s", (teacher[0],))
                    teacher_user_id = cursor.fetchone()[0]
                
                # 添加教师信息
                cursor.execute("""
                    INSERT INTO teacher (staff_id, user_id, name, sex, date_of_birth, professional_ranks, salary, dept_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                        user_id=%s, name=%s, sex=%s, date_of_birth=%s, 
                        professional_ranks=%s, salary=%s, dept_id=%s
                """, (
                    teacher[2], teacher_user_id, teacher[3], teacher[4], teacher[5], 
                    teacher[6], teacher[7], teacher[8],
                    teacher_user_id, teacher[3], teacher[4], teacher[5], 
                    teacher[6], teacher[7], teacher[8]
                ))
                conn.commit()
            except mysql.connector.Error as err:
                print(f"添加教师账户失败: {err}")
        
        # 4. 添加学生账户和信息
        students = [
            ('student1', 'student123', 'S20001', '张三', 'M', '2000-01-15', '北京', '13800000001', '01', 'active'),
            ('student2', 'student123', 'S20002', '李四', 'F', '2001-03-20', '上海', '13800000002', '01', 'active'),
            ('student3', 'student123', 'S20003', '王五', 'M', '2000-11-05', '广州', '13800000003', '02', 'active'),
            ('student4', 'student123', 'S20004', '赵六', 'F', '2001-07-25', '深圳', '13800000004', '03', 'active'),
            ('student5', 'student123', 'S20005', '钱七', 'M', '2000-05-10', '武汉', '13800000005', '04', 'active')
        ]
        
        for student in students:
            try:
                # 添加登录信息
                cursor.execute("""
                    INSERT INTO login_info (username, password, role)
                    VALUES (%s, %s, 'student')
                    ON DUPLICATE KEY UPDATE password=%s
                """, (student[0], student[1], student[1]))
                
                student_user_id = cursor.lastrowid
                if not student_user_id:
                    cursor.execute("SELECT user_id FROM login_info WHERE username=%s", (student[0],))
                    student_user_id = cursor.fetchone()[0]
                
                # 添加学生信息
                cursor.execute("""
                    INSERT INTO student (student_id, user_id, name, sex, date_of_birth, native_place, mobile_phone, dept_id, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                        user_id=%s, name=%s, sex=%s, date_of_birth=%s, 
                        native_place=%s, mobile_phone=%s, dept_id=%s, status=%s
                """, (
                    student[2], student_user_id, student[3], student[4], student[5], 
                    student[6], student[7], student[8], student[9],
                    student_user_id, student[3], student[4], student[5], 
                    student[6], student[7], student[8], student[9]
                ))
                conn.commit()
            except mysql.connector.Error as err:
                print(f"添加学生账户失败: {err}")
        
        # 5. 添加课程信息
        courses = [
            ('CS101', '计算机导论', 3, 40, '01'),
            ('CS201', '数据结构', 4, 48, '01'),
            ('CS301', '操作系统', 4, 52, '01'),
            ('EE101', '电路基础', 3, 40, '02'),
            ('EE201', '数字电路', 4, 48, '02'),
            ('MA101', '高等数学', 5, 60, '03'),
            ('MA201', '线性代数', 4, 48, '03'),
            ('PH101', '大学物理', 4, 52, '04'),
            ('EN101', '大学英语', 3, 40, '05')
        ]
        
        for course in courses:
            try:
                cursor.execute("""
                    INSERT INTO course (course_id, course_name, credit, credit_hours, dept_id)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                        course_name=%s, credit=%s, credit_hours=%s, dept_id=%s
                """, (
                    course[0], course[1], course[2], course[3], course[4],
                    course[1], course[2], course[3], course[4]
                ))
                conn.commit()
            except mysql.connector.Error as err:
                print(f"添加课程失败: {err}")
        
        # 6. 添加班级信息（课程与教师的关联）
        class_assignments = [
            (semester, 'CS101', 'T10001', f'{current_year}-09-01 08:00:00'),
            (semester, 'CS201', 'T10001', f'{current_year}-09-01 10:00:00'),
            (semester, 'CS301', 'T10002', f'{current_year}-09-01 14:00:00'),
            (semester, 'EE101', 'T10003', f'{current_year}-09-02 08:00:00'),
            (semester, 'EE201', 'T10003', f'{current_year}-09-02 10:00:00'),
            (semester, 'MA101', 'T10004', f'{current_year}-09-02 14:00:00'),
            (semester, 'MA201', 'T10004', f'{current_year}-09-03 08:00:00'),
            (semester, 'PH101', 'T10005', f'{current_year}-09-03 10:00:00'),
            (semester, 'EN101', 'T10001', f'{current_year}-09-03 14:00:00')
        ]
        
        for class_assignment in class_assignments:
            try:
                # 检查是否已存在，如果存在则更新，不存在则插入
                cursor.execute("""
                    SELECT 1 FROM class 
                    WHERE semester=%s AND course_id=%s AND staff_id=%s
                """, (class_assignment[0], class_assignment[1], class_assignment[2]))
                
                if cursor.fetchone():
                    cursor.execute("""
                        UPDATE class SET class_time=%s
                        WHERE semester=%s AND course_id=%s AND staff_id=%s
                    """, (
                        class_assignment[3], class_assignment[0], 
                        class_assignment[1], class_assignment[2]
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO class (semester, course_id, staff_id, class_time)
                        VALUES (%s, %s, %s, %s)
                    """, class_assignment)
                
                conn.commit()
            except mysql.connector.Error as err:
                print(f"添加班级信息失败: {err}")
        
        print("测试数据添加完成！")
        
        print("\n测试账户信息:")
        print("管理员: admin / admin123")
        print("教师: teacher1-5 / teacher123")
        print("学生: student1-5 / student123")
        
        print(f"\n当前学期: {semester}")
        print(f"可选课程: CS101, CS201, CS301, EE101, EE201, MA101, MA201, PH101, EN101")
        
    except mysql.connector.Error as err:
        print(f"连接数据库出错: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("数据库连接已关闭")

if __name__ == "__main__":
    add_test_data() 
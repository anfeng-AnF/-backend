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

def init_full_database():
    """初始化整个数据库及测试数据"""
    try:
        # 连接数据库
        print("连接数据库...")
        conn = mysql.connector.connect(host=DB_CONFIG['host'], user=DB_CONFIG['user'], password=DB_CONFIG['password'])
        cursor = conn.cursor()
        
        # 确保数据库存在
        print("确保数据库存在...")
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        print("创建数据库表...")
        # 创建 login_info 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_info (
                user_id INT NOT NULL AUTO_INCREMENT,
                username VARCHAR(100) NOT NULL,
                password VARCHAR(255) NOT NULL,
                role ENUM('admin', 'teacher', 'student') NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id),
                UNIQUE (username)
            ) AUTO_INCREMENT = 100000000
        ''')
        
        # 创建 department 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS department (
                dept_id CHAR(2) NOT NULL,
                dept_name VARCHAR(100) NOT NULL,
                address VARCHAR(255),
                phone_code VARCHAR(15),
                PRIMARY KEY (dept_id)
            )
        ''')
        
        # 创建 admin 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                admin_id INT NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
                role ENUM('superadmin', 'admin') NOT NULL DEFAULT 'admin',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (admin_id),
                FOREIGN KEY (user_id) REFERENCES login_info(user_id)
            )
        ''')
        
        # 创建 student 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student (
                student_id CHAR(8) NOT NULL,
                user_id INT NOT NULL,
                name VARCHAR(100) NOT NULL,
                sex ENUM('M', 'F') NOT NULL DEFAULT 'M',
                date_of_birth DATE NOT NULL DEFAULT '2000-01-01',
                native_place VARCHAR(100),
                mobile_phone VARCHAR(15),
                dept_id CHAR(2) NOT NULL,
                status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
                PRIMARY KEY (student_id),
                FOREIGN KEY (user_id) REFERENCES login_info(user_id),
                FOREIGN KEY (dept_id) REFERENCES department(dept_id)
            )
        ''')
        
        # 创建 teacher 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teacher (
                staff_id CHAR(8) NOT NULL,
                user_id INT NOT NULL,
                name VARCHAR(100) NOT NULL,
                sex ENUM('M', 'F') NOT NULL DEFAULT 'M',
                date_of_birth DATE NOT NULL DEFAULT '1980-01-01',
                professional_ranks VARCHAR(100),
                salary DECIMAL(10, 2),
                dept_id CHAR(2) NOT NULL,
                PRIMARY KEY (staff_id),
                FOREIGN KEY (user_id) REFERENCES login_info(user_id),
                FOREIGN KEY (dept_id) REFERENCES department(dept_id)
            )
        ''')
        
        # 创建 course 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS course (
                course_id CHAR(8) NOT NULL,
                course_name VARCHAR(100) NOT NULL,
                credit INT DEFAULT 4,
                credit_hours INT DEFAULT 40,
                dept_id CHAR(2) NOT NULL,
                PRIMARY KEY (course_id),
                FOREIGN KEY (dept_id) REFERENCES department(dept_id)
            )
        ''')
        
        # 创建 class 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS class (
                semester VARCHAR(20) NOT NULL,
                course_id CHAR(8) NOT NULL,
                staff_id CHAR(8) NOT NULL,
                class_time DATETIME NOT NULL,
                PRIMARY KEY (semester, course_id, staff_id),
                FOREIGN KEY (course_id) REFERENCES course(course_id),
                FOREIGN KEY (staff_id) REFERENCES teacher(staff_id)
            )
        ''')
        
        # 创建 course_selection 表
        cursor.execute('''
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
            )
        ''')
        
        # 创建 score_record 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS score_record (
                id INT AUTO_INCREMENT PRIMARY KEY,
                course_selection_id INT NOT NULL UNIQUE,
                usual_score DECIMAL(5,2),
                final_score DECIMAL(5,2),
                total_score DECIMAL(5,2),
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (course_selection_id) REFERENCES course_selection(id)
            )
        ''')
        
        # 创建 homework_log 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS homework_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                course_selection_id INT NOT NULL,
                title VARCHAR(255),
                description TEXT,
                submit_time DATETIME,
                score DECIMAL(5,2),
                attachment_url VARCHAR(255),
                FOREIGN KEY (course_selection_id) REFERENCES course_selection(id)
            )
        ''')
        
        # 创建 quiz_log 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                course_selection_id INT NOT NULL,
                quiz_name VARCHAR(255),
                quiz_date DATETIME,
                score DECIMAL(5,2),
                FOREIGN KEY (course_selection_id) REFERENCES course_selection(id)
            )
        ''')
        
        # 创建 user_activity_log 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity_log (
                log_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                action VARCHAR(100) NOT NULL,
                action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(50),
                FOREIGN KEY (user_id) REFERENCES login_info(user_id)
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX idx1 ON student (dept_id ASC, name DESC)')
        cursor.execute('CREATE INDEX idx2 ON course (course_name)')
        
        # 创建触发器：计算总成绩
        cursor.execute('''
            DROP TRIGGER IF EXISTS trg_score_record_before_insert
        ''')
        
        cursor.execute('''
            DROP TRIGGER IF EXISTS trg_score_record_before_update
        ''')
        
        cursor.execute('''
            CREATE TRIGGER trg_score_record_before_insert
            BEFORE INSERT ON score_record
            FOR EACH ROW
            BEGIN
                IF NEW.usual_score IS NOT NULL AND NEW.final_score IS NOT NULL THEN
                    SET NEW.total_score = NEW.usual_score * 0.4 + NEW.final_score * 0.6;
                END IF;
            END
        ''')
        
        cursor.execute('''
            CREATE TRIGGER trg_score_record_before_update
            BEFORE UPDATE ON score_record
            FOR EACH ROW
            BEGIN
                IF NEW.usual_score IS NOT NULL AND NEW.final_score IS NOT NULL THEN
                    SET NEW.total_score = NEW.usual_score * 0.4 + NEW.final_score * 0.6;
                END IF;
            END
        ''')
        
        # 添加初始测试数据
        print("添加测试数据...")
        
        # 添加院系数据
        print("添加院系数据...")
        departments = [
            ('01', '计算机科学与技术学院', 'A栋', '123-456-7890'),
            ('02', '电子信息工程学院', 'B栋', '123-456-7891'),
            ('03', '数学学院', 'C栋', '123-456-7892'),
            ('04', '物理学院', 'D栋', '123-456-7893'),
            ('05', '化学学院', 'E栋', '123-456-7894')
        ]
        
        for dept in departments:
            cursor.execute('''
                INSERT INTO department (dept_id, dept_name, address, phone_code)
                VALUES (%s, %s, %s, %s)
            ''', dept)
        
        # 添加用户账户
        print("添加用户账户...")
        users = [
            # Admin用户
            (None, 'admin', 'admin123', 'admin'),
            (None, 'superadmin', 'super123', 'admin'),
            
            # 教师用户
            (None, 'teacher1', 'teacher123', 'teacher'),
            (None, 'teacher2', 'teacher123', 'teacher'),
            (None, 'teacher3', 'teacher123', 'teacher'),
            (None, 'teacher4', 'teacher123', 'teacher'),
            (None, 'teacher5', 'teacher123', 'teacher'),
            
            # 学生用户
            (None, 'student1', 'student123', 'student'),
            (None, 'student2', 'student123', 'student'),
            (None, 'student3', 'student123', 'student'),
            (None, 'student4', 'student123', 'student'),
            (None, 'student5', 'student123', 'student'),
            (None, 'student6', 'student123', 'student'),
            (None, 'student7', 'student123', 'student'),
            (None, 'student8', 'student123', 'student'),
            (None, 'student9', 'student123', 'student'),
            (None, 'student10', 'student123', 'student')
        ]
        
        user_ids = {}
        for user in users:
            cursor.execute('''
                INSERT INTO login_info (user_id, username, password, role)
                VALUES (%s, %s, %s, %s)
            ''', user)
            
            # 获取自增的user_id
            if user[0] is None:
                cursor.execute("SELECT LAST_INSERT_ID()")
                user_id = cursor.fetchone()[0]
                user_ids[user[1]] = user_id
        
        # 添加管理员
        print("添加管理员...")
        cursor.execute('''
            INSERT INTO admin (user_id, role)
            VALUES (%s, %s)
        ''', (user_ids['admin'], 'admin'))
        
        cursor.execute('''
            INSERT INTO admin (user_id, role)
            VALUES (%s, %s)
        ''', (user_ids['superadmin'], 'superadmin'))
        
        # 添加教师
        print("添加教师...")
        teachers = [
            ('T1000001', user_ids['teacher1'], '张教授', 'M', '1975-05-10', '教授', 12000.00, '01'),
            ('T1000002', user_ids['teacher2'], '李副教授', 'F', '1980-03-15', '副教授', 10000.00, '01'),
            ('T1000003', user_ids['teacher3'], '王讲师', 'M', '1985-07-20', '讲师', 8000.00, '02'),
            ('T1000004', user_ids['teacher4'], '赵教授', 'F', '1978-11-25', '教授', 12000.00, '03'),
            ('T1000005', user_ids['teacher5'], '刘副教授', 'M', '1982-09-30', '副教授', 10000.00, '04')
        ]
        
        for teacher in teachers:
            cursor.execute('''
                INSERT INTO teacher (staff_id, user_id, name, sex, date_of_birth, professional_ranks, salary, dept_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', teacher)
        
        # 添加学生
        print("添加学生...")
        students = [
            ('S2023001', user_ids['student1'], '小明', 'M', '2000-01-15', '北京', '13812345601', '01', 'active'),
            ('S2023002', user_ids['student2'], '小红', 'F', '2001-03-20', '上海', '13812345602', '01', 'active'),
            ('S2023003', user_ids['student3'], '小张', 'M', '2000-05-25', '广州', '13812345603', '01', 'active'),
            ('S2023004', user_ids['student4'], '小李', 'F', '2001-07-30', '深圳', '13812345604', '02', 'active'),
            ('S2023005', user_ids['student5'], '小王', 'M', '2000-09-05', '南京', '13812345605', '02', 'active'),
            ('S2023006', user_ids['student6'], '小刘', 'F', '2001-11-10', '杭州', '13812345606', '02', 'active'),
            ('S2023007', user_ids['student7'], '小赵', 'M', '2000-02-15', '武汉', '13812345607', '03', 'active'),
            ('S2023008', user_ids['student8'], '小孙', 'F', '2001-04-20', '成都', '13812345608', '03', 'active'),
            ('S2023009', user_ids['student9'], '小钱', 'M', '2000-06-25', '西安', '13812345609', '04', 'active'),
            ('S2023010', user_ids['student10'], '小周', 'F', '2001-08-30', '重庆', '13812345610', '04', 'active')
        ]
        
        for student in students:
            cursor.execute('''
                INSERT INTO student (student_id, user_id, name, sex, date_of_birth, native_place, mobile_phone, dept_id, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', student)
        
        # 添加课程
        print("添加课程...")
        courses = [
            ('CS101', '程序设计基础', 4, 48, '01'),
            ('CS102', '数据结构', 4, 48, '01'),
            ('CS103', '操作系统', 3, 40, '01'),
            ('CS104', '数据库原理', 4, 48, '01'),
            ('CS105', '计算机网络', 3, 40, '01'),
            ('EE101', '电路分析基础', 4, 48, '02'),
            ('EE102', '模拟电子技术', 4, 48, '02'),
            ('EE103', '数字电子技术', 3, 40, '02'),
            ('MA101', '高等数学', 5, 64, '03'),
            ('MA102', '线性代数', 3, 40, '03'),
            ('MA103', '概率论与数理统计', 3, 40, '03'),
            ('PH101', '大学物理', 4, 48, '04'),
            ('CH101', '大学化学', 3, 40, '05')
        ]
        
        for course in courses:
            cursor.execute('''
                INSERT INTO course (course_id, course_name, credit, credit_hours, dept_id)
                VALUES (%s, %s, %s, %s, %s)
            ''', course)
        
        # 添加班级（课程安排）
        print("添加班级...")
        current_semester = '2023-2024-1'  # 当前学期
        previous_semester = '2022-2023-2'  # 上一学期
        
        # 添加当前学期的课程
        current_classes = [
            (current_semester, 'CS101', 'T1000001', '2023-09-01 08:00:00'),
            (current_semester, 'CS102', 'T1000002', '2023-09-01 10:00:00'),
            (current_semester, 'CS103', 'T1000001', '2023-09-02 08:00:00'),
            (current_semester, 'CS104', 'T1000002', '2023-09-02 10:00:00'),
            (current_semester, 'EE101', 'T1000003', '2023-09-03 08:00:00'),
            (current_semester, 'EE102', 'T1000003', '2023-09-03 10:00:00'),
            (current_semester, 'MA101', 'T1000004', '2023-09-04 08:00:00'),
            (current_semester, 'MA102', 'T1000004', '2023-09-04 10:00:00'),
            (current_semester, 'PH101', 'T1000005', '2023-09-05 08:00:00')
        ]
        
        # 添加上一学期的课程
        previous_classes = [
            (previous_semester, 'CS101', 'T1000001', '2023-02-01 08:00:00'),
            (previous_semester, 'CS102', 'T1000002', '2023-02-01 10:00:00'),
            (previous_semester, 'EE101', 'T1000003', '2023-02-02 08:00:00'),
            (previous_semester, 'MA101', 'T1000004', '2023-02-02 10:00:00'),
            (previous_semester, 'PH101', 'T1000005', '2023-02-03 08:00:00')
        ]
        
        classes = current_classes + previous_classes
        
        for class_info in classes:
            cursor.execute('''
                INSERT INTO class (semester, course_id, staff_id, class_time)
                VALUES (%s, %s, %s, %s)
            ''', class_info)
        
        # 添加选课记录
        print("添加选课记录...")
        
        # 定义学生与课程的选课关系
        # 格式：(学生ID, 学期, 课程ID, 教师ID)
        
        # 当前学期选课
        current_selections = []
        for i in range(1, 11):  # 10个学生
            student_id = f'S202300{i}' if i < 10 else f'S20230{i}'
            
            # 每个学生选3-5门课
            num_courses = random.randint(3, 5)
            available_courses = list(current_classes)
            random.shuffle(available_courses)
            
            for j in range(min(num_courses, len(available_courses))):
                class_info = available_courses[j]
                current_selections.append((student_id, class_info[0], class_info[1], class_info[2]))
        
        # 上一学期选课（带成绩）
        previous_selections = []
        for i in range(1, 11):  # 10个学生
            student_id = f'S202300{i}' if i < 10 else f'S20230{i}'
            
            # 每个学生选2-4门课
            num_courses = random.randint(2, 4)
            available_courses = list(previous_classes)
            random.shuffle(available_courses)
            
            for j in range(min(num_courses, len(available_courses))):
                class_info = available_courses[j]
                previous_selections.append((student_id, class_info[0], class_info[1], class_info[2]))
        
        # 插入所有选课记录
        selection_ids = {}  # 存储选课ID以便添加成绩等数据
        
        for selection in current_selections + previous_selections:
            cursor.execute('''
                INSERT INTO course_selection (student_id, semester, course_id, staff_id)
                VALUES (%s, %s, %s, %s)
            ''', selection)
            
            selection_id = cursor.lastrowid
            key = f"{selection[0]}_{selection[1]}_{selection[2]}"
            selection_ids[key] = selection_id
        
        # 为上一学期的选课添加成绩记录
        print("添加成绩记录...")
        for selection in previous_selections:
            key = f"{selection[0]}_{selection[1]}_{selection[2]}"
            selection_id = selection_ids[key]
            
            # 生成随机成绩
            usual_score = round(random.uniform(60, 95), 2)
            final_score = round(random.uniform(60, 95), 2)
            
            cursor.execute('''
                INSERT INTO score_record (course_selection_id, usual_score, final_score)
                VALUES (%s, %s, %s)
            ''', (selection_id, usual_score, final_score))
        
        # 为上一学期的选课添加作业记录
        print("添加作业记录...")
        for selection in previous_selections:
            key = f"{selection[0]}_{selection[1]}_{selection[2]}"
            selection_id = selection_ids[key]
            
            # 每门课程添加2-4个作业
            num_homeworks = random.randint(2, 4)
            for i in range(num_homeworks):
                submit_date = datetime(2023, 3, 1) + timedelta(days=i*14 + random.randint(0, 5))
                title = f"第{i+1}次作业"
                description = f"{selection[2]}课程的第{i+1}次作业，内容包括第{i+1}章的练习题。"
                score = round(random.uniform(70, 100), 2)
                
                cursor.execute('''
                    INSERT INTO homework_log (course_selection_id, title, description, submit_time, score)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (selection_id, title, description, submit_date, score))
        
        # 为上一学期的选课添加测验记录
        print("添加测验记录...")
        for selection in previous_selections:
            key = f"{selection[0]}_{selection[1]}_{selection[2]}"
            selection_id = selection_ids[key]
            
            # 每门课程添加1-3个测验
            num_quizzes = random.randint(1, 3)
            for i in range(num_quizzes):
                quiz_date = datetime(2023, 3, 15) + timedelta(days=i*21 + random.randint(0, 5))
                quiz_name = f"第{i+1}次课堂测验"
                score = round(random.uniform(60, 98), 2)
                
                cursor.execute('''
                    INSERT INTO quiz_log (course_selection_id, quiz_name, quiz_date, score)
                    VALUES (%s, %s, %s, %s)
                ''', (selection_id, quiz_name, quiz_date, score))
        
        # 添加用户活动日志
        print("添加用户活动日志...")
        activities = [
            (user_ids['admin'], '登录系统', '127.0.0.1'),
            (user_ids['admin'], '修改用户权限', '127.0.0.1'),
            (user_ids['teacher1'], '登录系统', '192.168.1.100'),
            (user_ids['teacher1'], '查看课程信息', '192.168.1.100'),
            (user_ids['teacher1'], '登记成绩', '192.168.1.100'),
            (user_ids['student1'], '登录系统', '192.168.1.200'),
            (user_ids['student1'], '选课', '192.168.1.200'),
            (user_ids['student1'], '查看成绩', '192.168.1.200')
        ]
        
        for activity in activities:
            cursor.execute('''
                INSERT INTO user_activity_log (user_id, action, ip_address)
                VALUES (%s, %s, %s)
            ''', activity)
        
        # 提交所有更改
        conn.commit()
        print("数据库初始化完成！所有测试数据已添加。")
        
    except mysql.connector.Error as err:
        print(f"错误: {err}")
        conn.rollback()
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("数据库连接已关闭。")

if __name__ == "__main__":
    init_full_database() 
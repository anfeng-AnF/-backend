import mysql.connector

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'course_selection_system'
}

def init_test_users():
    """初始化测试用户账户"""
    try:
        # 连接数据库
        print("连接数据库...")
        conn = mysql.connector.connect(host=DB_CONFIG['host'], user=DB_CONFIG['user'], password=DB_CONFIG['password'])
        cursor = conn.cursor()
        
        # 确保数据库存在
        print("确保数据库存在...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        # 确保login_info表存在
        print("确保login_info表存在...")
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
        
        # 确保department表存在
        print("确保department表存在...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS department (
                dept_id CHAR(2) NOT NULL,
                dept_name VARCHAR(100) NOT NULL,
                address VARCHAR(255),
                phone_code VARCHAR(15),
                PRIMARY KEY (dept_id)
            )
        ''')
        
        # 确保admin表存在
        print("确保admin表存在...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                admin_id INT NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
                role ENUM('superadmin', 'admin') NOT NULL DEFAULT 'admin',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (admin_id),
                KEY (user_id)
            )
        ''')
        
        # 确保student表存在
        print("确保student表存在...")
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
                KEY (user_id),
                KEY (dept_id)
            )
        ''')
        
        # 确保teacher表存在
        print("确保teacher表存在...")
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
                KEY (user_id),
                KEY (dept_id)
            )
        ''')
        
        # 添加基础院系数据
        print("添加基础院系数据...")
        departments = [
            ('01', '计算机科学与技术学院'),
            ('02', '电子信息工程学院'),
            ('03', '数学学院')
        ]
        
        for dept in departments:
            try:
                cursor.execute('''
                    INSERT INTO department (dept_id, dept_name)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE dept_name=%s
                ''', (dept[0], dept[1], dept[1]))
                print(f"院系 '{dept[1]}' {'添加' if cursor.rowcount == 1 else '更新'} 成功")
            except mysql.connector.Error as err:
                print(f"添加院系 '{dept[1]}' 失败: {err}")
        
        # 添加测试用户
        print("添加测试用户...")
        users = [
            ('admin', 'admin123', 'admin'),
            ('student1', 'student123', 'student'),
            ('teacher1', 'teacher123', 'teacher')
        ]
        
        for user in users:
            try:
                cursor.execute('''
                    INSERT INTO login_info (username, password, role)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE password=%s, role=%s
                ''', (user[0], user[1], user[2], user[1], user[2]))
                print(f"用户 '{user[0]}' {'添加' if cursor.rowcount == 1 else '更新'} 成功")
            except mysql.connector.Error as err:
                print(f"添加用户 '{user[0]}' 失败: {err}")
        
        # 添加admin用户到admin表
        print("添加admin用户到admin表...")
        cursor.execute("SELECT user_id FROM login_info WHERE username='admin'")
        admin_user_id = cursor.fetchone()
        
        if admin_user_id:
            try:
                cursor.execute('''
                    INSERT INTO admin (user_id, role)
                    VALUES (%s, 'admin')
                    ON DUPLICATE KEY UPDATE role='admin'
                ''', (admin_user_id[0],))
                print(f"管理员记录 {'添加' if cursor.rowcount == 1 else '更新'} 成功")
            except mysql.connector.Error as err:
                print(f"添加管理员记录失败: {err}")
        
        # 添加学生用户到student表
        print("添加学生用户到student表...")
        cursor.execute("SELECT user_id FROM login_info WHERE username='student1'")
        student_user_id = cursor.fetchone()
        
        if student_user_id:
            try:
                cursor.execute('''
                    INSERT INTO student (student_id, user_id, name, sex, date_of_birth, dept_id, status)
                    VALUES ('S20001', %s, '张三', 'M', '2000-01-01', '01', 'active')
                    ON DUPLICATE KEY UPDATE 
                        user_id=%s, name='张三', sex='M', date_of_birth='2000-01-01', 
                        dept_id='01', status='active'
                ''', (student_user_id[0], student_user_id[0]))
                print(f"学生记录 {'添加' if cursor.rowcount == 1 else '更新'} 成功")
            except mysql.connector.Error as err:
                print(f"添加学生记录失败: {err}")
        
        # 添加教师用户到teacher表
        print("添加教师用户到teacher表...")
        cursor.execute("SELECT user_id FROM login_info WHERE username='teacher1'")
        teacher_user_id = cursor.fetchone()
        
        if teacher_user_id:
            try:
                cursor.execute('''
                    INSERT INTO teacher (staff_id, user_id, name, sex, date_of_birth, professional_ranks, salary, dept_id)
                    VALUES ('T10001', %s, '李教授', 'M', '1980-01-01', '教授', 10000.00, '01')
                    ON DUPLICATE KEY UPDATE 
                        user_id=%s, name='李教授', sex='M', date_of_birth='1980-01-01', 
                        professional_ranks='教授', salary=10000.00, dept_id='01'
                ''', (teacher_user_id[0], teacher_user_id[0]))
                print(f"教师记录 {'添加' if cursor.rowcount == 1 else '更新'} 成功")
            except mysql.connector.Error as err:
                print(f"添加教师记录失败: {err}")
        
        conn.commit()
        print("测试用户初始化完成！")
        
        # 打印所有用户信息
        print("\n当前用户列表:")
        cursor.execute("SELECT user_id, username, password, role FROM login_info")
        users = cursor.fetchall()
        for user in users:
            print(f"ID: {user[0]}, 用户名: {user[1]}, 密码: {user[2]}, 角色: {user[3]}")
        
        print("\n验证student表:")
        cursor.execute("SELECT student_id, user_id, name FROM student")
        students = cursor.fetchall()
        for student in students:
            print(f"学号: {student[0]}, 用户ID: {student[1]}, 姓名: {student[2]}")
            
        print("\n验证teacher表:")
        cursor.execute("SELECT staff_id, user_id, name FROM teacher")
        teachers = cursor.fetchall()
        for teacher in teachers:
            print(f"工号: {teacher[0]}, 用户ID: {teacher[1]}, 姓名: {teacher[2]}")
        
    except mysql.connector.Error as err:
        print(f"连接数据库出错: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("数据库连接已关闭")

if __name__ == "__main__":
    init_test_users() 
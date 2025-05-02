import mysql.connector
from datetime import datetime
import argparse

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'course_selection_system'
}

def get_db_connection():
    """连接数据库"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"数据库连接错误: {err}")
        return None

def fetch_all_teachers():
    """获取所有教师信息"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.staff_id, t.name, d.dept_name 
            FROM teacher t
            JOIN department d ON t.dept_id = d.dept_id
            ORDER BY t.staff_id
        """)
        teachers = cursor.fetchall()
        cursor.close()
        conn.close()
        return teachers
    except mysql.connector.Error as err:
        print(f"查询教师信息出错: {err}")
        if conn.is_connected():
            conn.close()
        return []

def fetch_all_courses():
    """获取所有课程信息"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.course_id, c.course_name, d.dept_name
            FROM course c
            JOIN department d ON c.dept_id = d.dept_id
            ORDER BY c.course_id
        """)
        courses = cursor.fetchall()
        cursor.close()
        conn.close()
        return courses
    except mysql.connector.Error as err:
        print(f"查询课程信息出错: {err}")
        if conn.is_connected():
            conn.close()
        return []

def fetch_teacher_courses(staff_id):
    """获取教师当前的教授课程信息"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT cl.semester, c.course_id, c.course_name, cl.class_time
            FROM class cl
            JOIN course c ON cl.course_id = c.course_id
            WHERE cl.staff_id = %s
            ORDER BY cl.semester DESC, c.course_id
        """, (staff_id,))
        courses = cursor.fetchall()
        cursor.close()
        conn.close()
        return courses
    except mysql.connector.Error as err:
        print(f"查询教师课程信息出错: {err}")
        if conn.is_connected():
            conn.close()
        return []

def assign_course_to_teacher(staff_id, course_id, semester, class_time):
    """为教师分配课程"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 检查课程是否已存在
        cursor.execute("""
            SELECT 1 FROM class 
            WHERE semester=%s AND course_id=%s AND staff_id=%s
        """, (semester, course_id, staff_id))
        
        if cursor.fetchone():
            # 更新现有课程安排
            cursor.execute("""
                UPDATE class SET class_time=%s
                WHERE semester=%s AND course_id=%s AND staff_id=%s
            """, (class_time, semester, course_id, staff_id))
            print(f"已更新课程安排: 学期 {semester}, 课程 {course_id}, 教师 {staff_id}")
        else:
            # 插入新的课程安排
            cursor.execute("""
                INSERT INTO class (semester, course_id, staff_id, class_time)
                VALUES (%s, %s, %s, %s)
            """, (semester, course_id, staff_id, class_time))
            print(f"已添加新的课程安排: 学期 {semester}, 课程 {course_id}, 教师 {staff_id}")
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as err:
        print(f"分配课程出错: {err}")
        if conn.is_connected():
            conn.close()
        return False

def remove_course_from_teacher(staff_id, course_id, semester):
    """取消教师的课程分配"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 首先检查该课程是否有学生选课记录
        cursor.execute("""
            SELECT COUNT(*) FROM course_selection
            WHERE staff_id = %s AND course_id = %s AND semester = %s
        """, (staff_id, course_id, semester))
        
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"无法移除课程安排: 学期 {semester}, 课程 {course_id}, 教师 {staff_id}")
            print(f"原因: 该课程已有 {count} 名学生选课")
            cursor.close()
            conn.close()
            return False
        
        # 删除课程安排
        cursor.execute("""
            DELETE FROM class
            WHERE semester = %s AND course_id = %s AND staff_id = %s
        """, (semester, course_id, staff_id))
        
        if cursor.rowcount > 0:
            print(f"已移除课程安排: 学期 {semester}, 课程 {course_id}, 教师 {staff_id}")
            conn.commit()
            cursor.close()
            conn.close()
            return True
        else:
            print(f"未找到课程安排: 学期 {semester}, 课程 {course_id}, 教师 {staff_id}")
            cursor.close()
            conn.close()
            return False
    except mysql.connector.Error as err:
        print(f"移除课程出错: {err}")
        if conn.is_connected():
            conn.close()
        return False

def create_new_semester(semester_name):
    """创建新学期"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 获取当前所有学期
        cursor.execute("SELECT DISTINCT semester FROM class")
        semesters = [row[0] for row in cursor.fetchall()]
        
        if semester_name in semesters:
            print(f"学期 '{semester_name}' 已存在")
            cursor.close()
            conn.close()
            return False
        
        # 创建新学期不需要在数据库中特别操作
        # 仅当有课程或选课记录时，数据库中才会有该学期的记录
        print(f"新学期 '{semester_name}' 已创建，可以开始为教师分配课程")
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as err:
        print(f"创建学期出错: {err}")
        if conn.is_connected():
            conn.close()
        return False

def list_all_semesters():
    """获取所有学期"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT semester FROM class ORDER BY semester DESC")
        semesters = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return semesters
    except mysql.connector.Error as err:
        print(f"查询所有学期出错: {err}")
        if conn.is_connected():
            conn.close()
        return []

def interactive_mode():
    """交互式模式运行脚本"""
    print("=" * 60)
    print("教师课程管理系统")
    print("=" * 60)
    
    while True:
        print("\n请选择操作:")
        print("1. 查看所有教师")
        print("2. 查看所有课程")
        print("3. 查看教师的课程安排")
        print("4. 为教师分配课程")
        print("5. 取消教师的课程分配")
        print("6. 创建新学期")
        print("7. 查看所有学期")
        print("0. 退出")
        
        choice = input("\n请输入选项 (0-7): ")
        
        if choice == '0':
            print("退出系统")
            break
        
        elif choice == '1':
            teachers = fetch_all_teachers()
            print("\n所有教师:")
            print("-" * 50)
            print(f"{'工号':<10} | {'姓名':<15} | {'院系':<20}")
            print("-" * 50)
            for teacher in teachers:
                print(f"{teacher['staff_id']:<10} | {teacher['name']:<15} | {teacher['dept_name']:<20}")
        
        elif choice == '2':
            courses = fetch_all_courses()
            print("\n所有课程:")
            print("-" * 60)
            print(f"{'课程号':<10} | {'课程名称':<25} | {'开课院系':<20}")
            print("-" * 60)
            for course in courses:
                print(f"{course['course_id']:<10} | {course['course_name']:<25} | {course['dept_name']:<20}")
        
        elif choice == '3':
            staff_id = input("请输入教师工号: ")
            teacher_courses = fetch_teacher_courses(staff_id)
            
            if not teacher_courses:
                print(f"教师 {staff_id} 没有课程安排或工号不存在")
                continue
                
            print(f"\n教师 {staff_id} 的课程安排:")
            print("-" * 75)
            print(f"{'学期':<12} | {'课程号':<10} | {'课程名称':<25} | {'上课时间':<20}")
            print("-" * 75)
            for course in teacher_courses:
                print(f"{course['semester']:<12} | {course['course_id']:<10} | {course['course_name']:<25} | {course['class_time']}")
        
        elif choice == '4':
            staff_id = input("请输入教师工号: ")
            course_id = input("请输入课程号: ")
            semester = input("请输入学期 (格式如 2023-2024-1): ")
            class_time = input("请输入上课时间 (格式如 2023-09-01 10:00:00): ")
            
            success = assign_course_to_teacher(staff_id, course_id, semester, class_time)
            if success:
                print("课程分配成功!")
            else:
                print("课程分配失败!")
        
        elif choice == '5':
            staff_id = input("请输入教师工号: ")
            course_id = input("请输入课程号: ")
            semester = input("请输入学期 (格式如 2023-2024-1): ")
            
            success = remove_course_from_teacher(staff_id, course_id, semester)
            if success:
                print("课程取消成功!")
            else:
                print("课程取消失败!")
        
        elif choice == '6':
            semester_name = input("请输入新学期名称 (格式如 2023-2024-1): ")
            success = create_new_semester(semester_name)
            if success:
                print("学期创建成功!")
            else:
                print("学期创建失败!")
        
        elif choice == '7':
            semesters = list_all_semesters()
            print("\n所有学期:")
            print("-" * 20)
            for semester in semesters:
                print(semester)
            print("-" * 20)
        
        else:
            print("无效选项，请重新选择")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='教师课程管理工具')
    parser.add_argument('--list-teachers', action='store_true', help='列出所有教师')
    parser.add_argument('--list-courses', action='store_true', help='列出所有课程')
    parser.add_argument('--list-semesters', action='store_true', help='列出所有学期')
    parser.add_argument('--teacher-courses', metavar='STAFF_ID', help='查看指定教师的课程')
    parser.add_argument('--assign', nargs=4, metavar=('STAFF_ID', 'COURSE_ID', 'SEMESTER', 'CLASS_TIME'), 
                        help='分配课程给教师')
    parser.add_argument('--remove', nargs=3, metavar=('STAFF_ID', 'COURSE_ID', 'SEMESTER'),
                        help='取消教师的课程分配')
    parser.add_argument('--new-semester', metavar='SEMESTER_NAME', help='创建新学期')
    
    args = parser.parse_args()
    
    # 如果没有参数，则进入交互模式
    if len(vars(args)) == 0 or all(v is None or v is False for v in vars(args).values()):
        interactive_mode()
        return
    
    # 处理命令行参数
    if args.list_teachers:
        teachers = fetch_all_teachers()
        print("\n所有教师:")
        for teacher in teachers:
            print(f"{teacher['staff_id']} | {teacher['name']} | {teacher['dept_name']}")
    
    if args.list_courses:
        courses = fetch_all_courses()
        print("\n所有课程:")
        for course in courses:
            print(f"{course['course_id']} | {course['course_name']} | {course['dept_name']}")
    
    if args.list_semesters:
        semesters = list_all_semesters()
        print("\n所有学期:")
        for semester in semesters:
            print(semester)
    
    if args.teacher_courses:
        courses = fetch_teacher_courses(args.teacher_courses)
        print(f"\n教师 {args.teacher_courses} 的课程:")
        for course in courses:
            print(f"{course['semester']} | {course['course_id']} | {course['course_name']} | {course['class_time']}")
    
    if args.assign:
        success = assign_course_to_teacher(*args.assign)
        if success:
            print("课程分配成功!")
        else:
            print("课程分配失败!")
    
    if args.remove:
        success = remove_course_from_teacher(*args.remove)
        if success:
            print("课程取消成功!")
        else:
            print("课程取消失败!")
    
    if args.new_semester:
        success = create_new_semester(args.new_semester)
        if success:
            print("学期创建成功!")
        else:
            print("学期创建失败!")

if __name__ == "__main__":
    main() 
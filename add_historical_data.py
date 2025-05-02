import mysql.connector
from datetime import datetime

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'course_selection_system'
}

def add_historical_data():
    """向数据库添加历史数据，包括2023-2024学期的教师课程和学生选课记录"""
    try:
        # 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 设置历史学期
        historical_semester = "2023-2024-2"  # 2023-2024学年第二学期
        
        print(f"添加 {historical_semester} 学期历史数据...")
        
        # 添加班级信息（课程与教师的关联）- 2023-2024学期
        class_assignments = [
            (historical_semester, 'CS101', 'T10001', '2024-02-01 08:00:00'),
            (historical_semester, 'CS201', 'T10001', '2024-02-01 10:00:00'),
            (historical_semester, 'CS301', 'T10002', '2024-02-01 14:00:00'),
            (historical_semester, 'EE101', 'T10003', '2024-02-02 08:00:00'),
            (historical_semester, 'EE201', 'T10003', '2024-02-02 10:00:00'),
            (historical_semester, 'MA101', 'T10004', '2024-02-02 14:00:00'),
            (historical_semester, 'MA201', 'T10004', '2024-02-03 08:00:00'),
            (historical_semester, 'PH101', 'T10005', '2024-02-03 10:00:00'),
            (historical_semester, 'EN101', 'T10001', '2024-02-03 14:00:00')
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
        
        # 添加学生选课记录
        course_selections = [
            ('S20001', historical_semester, 'CS101', 'T10001'),
            ('S20001', historical_semester, 'CS201', 'T10001'),
            ('S20001', historical_semester, 'MA101', 'T10004'),
            ('S20002', historical_semester, 'CS101', 'T10001'),
            ('S20002', historical_semester, 'EE101', 'T10003'),
            ('S20002', historical_semester, 'MA101', 'T10004'),
            ('S20003', historical_semester, 'EE101', 'T10003'),
            ('S20003', historical_semester, 'EE201', 'T10003'),
            ('S20003', historical_semester, 'PH101', 'T10005'),
            ('S20004', historical_semester, 'MA101', 'T10004'),
            ('S20004', historical_semester, 'MA201', 'T10004'),
            ('S20004', historical_semester, 'EN101', 'T10001'),
            ('S20005', historical_semester, 'PH101', 'T10005'),
            ('S20005', historical_semester, 'EN101', 'T10001'),
            ('S20005', historical_semester, 'CS301', 'T10002')
        ]
        
        for selection in course_selections:
            try:
                # 检查是否已存在
                cursor.execute("""
                    SELECT id FROM course_selection 
                    WHERE student_id = %s AND semester = %s AND course_id = %s
                """, (selection[0], selection[1], selection[2]))
                
                result = cursor.fetchone()
                if result:
                    print(f"选课记录已存在: {selection}")
                    continue
                
                # 插入新的选课记录
                cursor.execute("""
                    INSERT INTO course_selection (student_id, semester, course_id, staff_id)
                    VALUES (%s, %s, %s, %s)
                """, selection)
                
                # 获取插入的选课ID
                course_selection_id = cursor.lastrowid
                
                # 随机生成一些成绩记录
                import random
                usual_score = round(random.uniform(60, 98), 1)
                final_score = round(random.uniform(60, 98), 1)
                
                # 添加成绩记录
                cursor.execute("""
                    INSERT INTO score_record (course_selection_id, usual_score, final_score)
                    VALUES (%s, %s, %s)
                """, (course_selection_id, usual_score, final_score))
                
                conn.commit()
            except mysql.connector.Error as err:
                print(f"添加选课记录失败: {err}")
        
        print("历史数据添加完成！")
        print(f"\n历史学期: {historical_semester}")
        print("已为所有教师添加历史课程及学生成绩数据")
        
    except mysql.connector.Error as err:
        print(f"连接数据库出错: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("数据库连接已关闭")

if __name__ == "__main__":
    add_historical_data() 
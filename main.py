from flask import Flask, request, jsonify, make_response
try:
    from flask_cors import CORS
    cors_available = True
except ImportError:
    cors_available = False
import mysql.connector
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import os
import re

app = Flask(__name__)

# Setup CORS if available
if cors_available:
    CORS(app)
else:
    # Manual CORS handling if flask_cors is not available
    @app.after_request
    def add_cors_headers(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    
    @app.route('/', methods=['OPTIONS'])
    @app.route('/<path:path>', methods=['OPTIONS'])
    def options_handler(path=None):
        return make_response('', 200)

# MySQL configurations
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'course_selection_system'
}

# Create connection pool
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Course selection configuration - 更新为当前时间到两个月后
today = datetime.now()
COURSE_SELECTION_START = today
COURSE_SELECTION_END = today + timedelta(days=60)  # 两个月后截止
MAX_STUDENTS_PER_COURSE = 50

# Add JWT support for authentication
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key
jwt = JWTManager(app)

# Error handler
@app.errorhandler(Exception)
def handle_error(error):
    print(f"API错误: {str(error)}")
    response = {
        "success": False,
        "error": str(error)
    }
    return jsonify(response), 500

# Login route
@app.route('/api/login', methods=['POST'])
def login():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        print(f"尝试登录: 用户名 = '{username}', 密码 = '{password}'")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 首先检查基本登录信息
        query = '''
            SELECT * FROM login_info
            WHERE username = %s AND password = %s
        '''
        
        print(f"执行基本登录查询...")
        cursor.execute(query, (username, password))
        user = cursor.fetchall()  # 使用fetchall确保所有结果被消费
        
        if not user or len(user) == 0:
            print(f"登录失败: 用户名或密码不正确")
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
        
        user = user[0]  # 获取第一个用户
        print(f"用户验证成功: ID = {user['user_id']}, 角色 = {user['role']}")
        
        # 根据角色获取额外信息
        role_id = None
        name = None
        
        if user['role'] == 'student':
            try:
                cursor.execute('''
                    SELECT student_id, name FROM student WHERE user_id = %s
                ''', (user['user_id'],))
                student_info = cursor.fetchall()
                if student_info and len(student_info) > 0:
                    student_info = student_info[0]
                    role_id = student_info['student_id']
                    name = student_info['name']
                    print(f"获取到学生信息: 学号 = {role_id}, 姓名 = {name}")
                else:
                    print(f"学生记录不存在，使用默认值")
                    role_id = f"S{user['user_id']}"
                    name = f"Student {user['user_id']}"
            except Exception as e:
                print(f"查询学生信息出错: {str(e)}")
                role_id = f"S{user['user_id']}"
                name = f"Student {user['user_id']}"
        
        elif user['role'] == 'teacher':
            try:
                cursor.execute('''
                    SELECT staff_id, name FROM teacher WHERE user_id = %s
                ''', (user['user_id'],))
                teacher_info = cursor.fetchall()
                if teacher_info and len(teacher_info) > 0:
                    teacher_info = teacher_info[0]
                    role_id = teacher_info['staff_id']
                    name = teacher_info['name']
                    print(f"获取到教师信息: 工号 = {role_id}, 姓名 = {name}")
                else:
                    print(f"教师记录不存在，使用默认值")
                    role_id = f"T{user['user_id']}"
                    name = f"Teacher {user['user_id']}"
            except Exception as e:
                print(f"查询教师信息出错: {str(e)}")
                role_id = f"T{user['user_id']}"
                name = f"Teacher {user['user_id']}"
        
        elif user['role'] == 'admin':
            try:
                cursor.execute('''
                    SELECT admin_id FROM admin WHERE user_id = %s
                ''', (user['user_id'],))
                admin_info = cursor.fetchall()
                if admin_info and len(admin_info) > 0:
                    admin_info = admin_info[0]
                    role_id = admin_info['admin_id']
                    print(f"获取到管理员信息: ID = {role_id}")
                else:
                    print(f"管理员记录不存在，使用默认值")
                    role_id = user['user_id']
                name = "Administrator"
            except Exception as e:
                print(f"查询管理员信息出错: {str(e)}")
                role_id = user['user_id']
                name = "Administrator"
                
        print(f"最终用户信息: ID = {user['user_id']}, 角色 = {user['role']}, 角色ID = {role_id}, 姓名 = {name}")
        
        # 创建token并返回用户信息
        user_data = {
            "user_id": user['user_id'],
            "role": user['role'],
            "role_id": role_id,
            "name": name
        }
        
        access_token = create_access_token(identity=user_data)
        print(f"登录成功，已生成token")
        
        return jsonify({
            "success": True,
            "token": access_token,
            "user": user_data
        })
        
    except Exception as e:
        print(f"登录异常: {str(e)}")
        return handle_error(e)
    finally:
        # 确保无论如何都关闭游标和连接
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# Protected route example
@app.route('/api/courses', methods=['GET'])
def get_courses():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT c.*, d.dept_name,
                   GROUP_CONCAT(DISTINCT t.name) as teachers,
                   GROUP_CONCAT(DISTINCT t.staff_id) as staff_ids
            FROM course c 
            JOIN department d ON c.dept_id = d.dept_id
            LEFT JOIN class cl ON c.course_id = cl.course_id
            LEFT JOIN teacher t ON cl.staff_id = t.staff_id
            GROUP BY c.course_id
        ''')
        courses = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "data": courses})
    except Exception as e:
        return handle_error(e)

# 新增: 课程高级搜索功能
@app.route('/api/courses/search', methods=['GET'])
def search_courses():
    try:
        # 获取查询参数
        course_id = request.args.get('course_id', '')
        course_name = request.args.get('course_name', '')
        dept_id = request.args.get('dept_id', '')
        credit = request.args.get('credit', '')
        teacher_name = request.args.get('teacher_name', '')
        semester = request.args.get('semester', '')
        
        # 构建基础查询
        query = '''
            SELECT c.*, d.dept_name,
                   GROUP_CONCAT(DISTINCT t.name) as teachers,
                   GROUP_CONCAT(DISTINCT t.staff_id) as staff_ids,
                   GROUP_CONCAT(DISTINCT cl.semester) as semesters
            FROM course c 
            JOIN department d ON c.dept_id = d.dept_id
            LEFT JOIN class cl ON c.course_id = cl.course_id
            LEFT JOIN teacher t ON cl.staff_id = t.staff_id
        '''
        
        # 构建 WHERE 子句
        conditions = []
        params = []
        
        if course_id:
            conditions.append("c.course_id LIKE %s")
            params.append(f"%{course_id}%")
            
        if course_name:
            conditions.append("c.course_name LIKE %s")
            params.append(f"%{course_name}%")
            
        if dept_id:
            conditions.append("c.dept_id = %s")
            params.append(dept_id)
            
        if credit:
            conditions.append("c.credit = %s")
            params.append(credit)
            
        if teacher_name:
            conditions.append("t.name LIKE %s")
            params.append(f"%{teacher_name}%")
            
        if semester:
            conditions.append("cl.semester = %s")
            params.append(semester)
            
        # 添加 WHERE 子句（如果有条件）
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        # 添加分组
        query += " GROUP BY c.course_id"
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        courses = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "data": courses})
    except Exception as e:
        return handle_error(e)

# Course selection routes
@app.route('/api/course-selection', methods=['POST'])
def select_course():
    try:
        # Check if course selection is open
        now = datetime.now()
        if now < COURSE_SELECTION_START or now > COURSE_SELECTION_END:
            return jsonify({
                "success": False,
                "message": f"Course selection is only available between {COURSE_SELECTION_START} and {COURSE_SELECTION_END}"
            })

        data = request.get_json()
        student_id = data.get('student_id')
        semester = data.get('semester')
        course_id = data.get('course_id')
        staff_id = data.get('staff_id')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if already selected
        cursor.execute('''
            SELECT * FROM course_selection 
            WHERE student_id = %s AND semester = %s AND course_id = %s
        ''', (student_id, semester, course_id))
        
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Course already selected"})

        # Check course capacity
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM course_selection
            WHERE course_id = %s AND semester = %s
        ''', (course_id, semester))
        
        result = cursor.fetchone()
        if result['count'] >= MAX_STUDENTS_PER_COURSE:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Course is full"})

        # Insert new selection
        cursor.execute('''
            INSERT INTO course_selection (student_id, semester, course_id, staff_id)
            VALUES (%s, %s, %s, %s)
        ''', (student_id, semester, course_id, staff_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "message": "Course selected successfully"})
    except Exception as e:
        return handle_error(e)

# 新增: 退课功能
@app.route('/api/course-withdrawal', methods=['DELETE'])
def withdraw_course():
    try:
        # Check if course selection is open
        now = datetime.now()
        if now < COURSE_SELECTION_START or now > COURSE_SELECTION_END:
            return jsonify({
                "success": False,
                "message": f"Course withdrawal is only available between {COURSE_SELECTION_START} and {COURSE_SELECTION_END}"
            })

        data = request.get_json()
        student_id = data.get('student_id')
        semester = data.get('semester')
        course_id = data.get('course_id')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if the course was selected
        cursor.execute('''
            SELECT id FROM course_selection 
            WHERE student_id = %s AND semester = %s AND course_id = %s
        ''', (student_id, semester, course_id))
        
        selection = cursor.fetchone()
        if not selection:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Course not found in your selections"})

        # Check if grades already exist
        cursor.execute('''
            SELECT * FROM score_record 
            WHERE course_selection_id = %s
        ''', (selection['id'],))
        
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Cannot withdraw from a course that has grades recorded"})

        # Delete the selection
        cursor.execute('''
            DELETE FROM course_selection 
            WHERE id = %s
        ''', (selection['id'],))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "message": "Course withdrawn successfully"})
    except Exception as e:
        return handle_error(e)

@app.route('/api/student/<student_id>/courses', methods=['GET'])
def get_student_courses(student_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT cs.*, c.course_name, c.credit, t.name as teacher_name
            FROM course_selection cs
            JOIN course c ON cs.course_id = c.course_id
            JOIN teacher t ON cs.staff_id = t.staff_id
            WHERE cs.student_id = %s
        ''', [student_id])
        courses = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "data": courses})
    except Exception as e:
        return handle_error(e)

@app.route('/api/student/<student_id>/scores', methods=['GET'])
def get_student_scores(student_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT cs.*, c.course_name, sr.usual_score, sr.final_score, sr.total_score
            FROM course_selection cs
            JOIN course c ON cs.course_id = c.course_id
            LEFT JOIN score_record sr ON cs.id = sr.course_selection_id
            WHERE cs.student_id = %s
        ''', [student_id])
        scores = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "data": scores})
    except Exception as e:
        return handle_error(e)

# Teacher routes
@app.route('/api/teacher/<staff_id>/courses', methods=['GET'])
def get_teacher_courses(staff_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT c.*, cl.semester, d.dept_name
            FROM course c
            JOIN class cl ON c.course_id = cl.course_id
            JOIN department d ON c.dept_id = d.dept_id
            WHERE cl.staff_id = %s
        ''', [staff_id])
        courses = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "data": courses})
    except Exception as e:
        return handle_error(e)

# 新增: 获取教师的所有学期信息
@app.route('/api/teacher/<staff_id>/semesters', methods=['GET'])
def get_teacher_semesters(staff_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT DISTINCT semester 
            FROM class
            WHERE staff_id = %s
            ORDER BY semester DESC
        ''', [staff_id])
        semesters = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "data": semesters})
    except Exception as e:
        return handle_error(e)

# 新增: 获取指定学期的教师课程
@app.route('/api/teacher/<staff_id>/semester/<semester>/courses', methods=['GET'])
def get_teacher_semester_courses(staff_id, semester):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT c.*, cl.semester, d.dept_name
            FROM course c
            JOIN class cl ON c.course_id = cl.course_id
            JOIN department d ON c.dept_id = d.dept_id
            WHERE cl.staff_id = %s AND cl.semester = %s
        ''', (staff_id, semester))
        courses = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "data": courses})
    except Exception as e:
        return handle_error(e)

@app.route('/api/teacher/course/<course_id>/semester/<semester>/students', methods=['GET'])
def get_course_students(course_id, semester):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT s.student_id, s.name, sr.usual_score, sr.final_score, sr.total_score
            FROM course_selection cs
            JOIN student s ON cs.student_id = s.student_id
            LEFT JOIN score_record sr ON cs.id = sr.course_selection_id
            WHERE cs.course_id = %s AND cs.semester = %s
        ''', (course_id, semester))
        students = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "data": students})
    except Exception as e:
        return handle_error(e)

@app.route('/api/teacher/grades', methods=['POST'])
def update_grades():
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        for grade in data['grades']:
            # Get course_selection_id
            cursor.execute('''
                SELECT id FROM course_selection
                WHERE student_id = %s AND course_id = %s AND semester = %s
            ''', (grade['student_id'], data['course_id'], data['semester']))
            
            cs_result = cursor.fetchone()
            if not cs_result:
                continue

            # Check if score record exists
            cursor.execute('''
                SELECT * FROM score_record
                WHERE course_selection_id = %s
            ''', (cs_result['id'],))
            
            if cursor.fetchone():
                # Update existing record
                cursor.execute('''
                    UPDATE score_record
                    SET usual_score = %s, final_score = %s
                    WHERE course_selection_id = %s
                ''', (grade['usual_score'], grade['final_score'], cs_result['id']))
            else:
                # Insert new record
                cursor.execute('''
                    INSERT INTO score_record (course_selection_id, usual_score, final_score)
                    VALUES (%s, %s, %s)
                ''', (cs_result['id'], grade['usual_score'], grade['final_score']))

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Grades updated successfully"})
    except Exception as e:
        return handle_error(e)

# Statistics routes
@app.route('/api/admin/statistics', methods=['GET'])
def admin_statistics():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get department statistics
        cursor.execute('''
            SELECT d.dept_name,
                   COUNT(DISTINCT c.course_id) as course_count,
                   COUNT(DISTINCT s.student_id) as student_count,
                   COUNT(DISTINCT t.staff_id) as teacher_count
            FROM department d
            LEFT JOIN course c ON d.dept_id = c.dept_id
            LEFT JOIN student s ON d.dept_id = s.dept_id
            LEFT JOIN teacher t ON d.dept_id = t.dept_id
            GROUP BY d.dept_id
        ''')
        dept_stats = cursor.fetchall()
        
        # Get course selection statistics
        cursor.execute('''
            SELECT c.course_id, c.course_name,
                   COUNT(cs.student_id) as student_count,
                   AVG(COALESCE(sr.total_score, 0)) as avg_score
            FROM course c
            LEFT JOIN course_selection cs ON c.course_id = cs.course_id
            LEFT JOIN score_record sr ON cs.id = sr.course_selection_id
            GROUP BY c.course_id
        ''')
        course_stats = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return jsonify({
            "success": True,
            "data": {
                "department_statistics": dept_stats,
                "course_statistics": course_stats
            }
        })
    except Exception as e:
        return handle_error(e)

@app.route('/api/teacher/<staff_id>/statistics', methods=['GET'])
def teacher_statistics(staff_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get teacher's courses statistics
        cursor.execute('''
            SELECT c.course_id, c.course_name, cl.semester,
                   COUNT(cs.student_id) as student_count,
                   AVG(COALESCE(sr.usual_score, 0)) as avg_usual_score,
                   AVG(COALESCE(sr.final_score, 0)) as avg_final_score,
                   AVG(COALESCE(sr.total_score, 0)) as avg_total_score,
                   MIN(COALESCE(sr.total_score, 0)) as min_score,
                   MAX(COALESCE(sr.total_score, 0)) as max_score
            FROM class cl
            JOIN course c ON cl.course_id = c.course_id
            LEFT JOIN course_selection cs ON (cl.course_id = cs.course_id AND cl.semester = cs.semester)
            LEFT JOIN score_record sr ON cs.id = sr.course_selection_id
            WHERE cl.staff_id = %s
            GROUP BY c.course_id, cl.semester
        ''', [staff_id])
        course_stats = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return jsonify({
            "success": True,
            "data": {
                "course_statistics": course_stats
            }
        })
    except Exception as e:
        return handle_error(e)

@app.route('/api/student/<student_id>/statistics', methods=['GET'])
def student_statistics(student_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get student's academic statistics
        cursor.execute('''
            SELECT cs.semester,
                   COUNT(cs.course_id) as course_count,
                   SUM(c.credit) as total_credits,
                   AVG(sr.total_score) as avg_score,
                   SUM(CASE WHEN sr.total_score >= 60 THEN c.credit ELSE 0 END) as earned_credits
            FROM course_selection cs
            JOIN course c ON cs.course_id = c.course_id
            LEFT JOIN score_record sr ON cs.id = sr.course_selection_id
            WHERE cs.student_id = %s
            GROUP BY cs.semester
        ''', [student_id])
        semester_stats = cursor.fetchall()
        
        # Get GPA calculation
        cursor.execute('''
            SELECT AVG(
                CASE 
                    WHEN sr.total_score >= 90 THEN 4.0
                    WHEN sr.total_score >= 80 THEN 3.0
                    WHEN sr.total_score >= 70 THEN 2.0
                    WHEN sr.total_score >= 60 THEN 1.0
                    ELSE 0
                END
            ) as gpa
            FROM course_selection cs
            JOIN score_record sr ON cs.id = sr.course_selection_id
            WHERE cs.student_id = %s
        ''', [student_id])
        gpa_stats = cursor.fetchone()
        
        cursor.close()
        conn.close()
        return jsonify({
            "success": True,
            "data": {
                "semester_statistics": semester_stats,
                "gpa": gpa_stats['gpa'] if gpa_stats and gpa_stats['gpa'] else 0
            }
        })
    except Exception as e:
        return handle_error(e)

# Admin routes
@app.route('/api/admin/courses', methods=['GET', 'POST'])
def admin_courses():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'GET':
            cursor.execute('''
                SELECT c.*, d.dept_name
                FROM course c
                JOIN department d ON c.dept_id = d.dept_id
            ''')
            courses = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify({"success": True, "data": courses})
        
        elif request.method == 'POST':
            data = request.get_json()
            cursor.execute('''
                INSERT INTO course (course_id, course_name, credit, credit_hours, dept_id)
                VALUES (%s, %s, %s, %s, %s)
            ''', (data['course_id'], data['course_name'], data['credit'], 
                 data.get('credit_hours', data['credit'] * 10), data['dept_id']))
            
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({"success": True, "message": "Course added successfully"})
            
    except Exception as e:
        return handle_error(e)

@app.route('/api/admin/departments', methods=['GET'])
def get_departments():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM department')
        departments = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "data": departments})
    except Exception as e:
        return handle_error(e)

@app.route('/api/admin/teachers', methods=['GET'])
def get_all_teachers():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT t.staff_id, t.name, d.dept_name, t.professional_ranks
            FROM teacher t
            JOIN department d ON t.dept_id = d.dept_id
            ORDER BY t.staff_id
        ''')
        teachers = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "data": teachers})
    except Exception as e:
        return handle_error(e)

@app.route('/api/admin/semesters', methods=['GET'])
def get_all_semesters():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT DISTINCT semester 
            FROM class
            ORDER BY semester DESC
        ''')
        semesters = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "data": semesters})
    except Exception as e:
        return handle_error(e)

@app.route('/api/admin/semesters', methods=['POST'])
def create_semester():
    try:
        data = request.get_json()
        semester = data.get('semester')
        
        if not semester:
            return jsonify({"success": False, "message": "学期名称不能为空"}), 400
        
        # 验证学期格式是否正确
        if not re.match(r'^\d{4}-\d{4}-[12]$', semester):
            return jsonify({"success": False, "message": "学期格式不正确，应为：yyyy-yyyy-n"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 检查学期是否已存在
        cursor.execute("SELECT 1 FROM class WHERE semester = %s LIMIT 1", [semester])
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "该学期已存在"}), 400
        
        # 新学期的创建不需要在数据库中特别操作
        # 它将在添加该学期的课程时自动创建
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True, 
            "message": f"学期 {semester} 已创建",
            "data": {"semester": semester}
        })
    except Exception as e:
        return handle_error(e)

@app.route('/api/admin/assign-course', methods=['POST'])
def assign_course():
    try:
        data = request.get_json()
        staff_id = data.get('staff_id')
        course_id = data.get('course_id')
        semester = data.get('semester')
        class_time = data.get('class_time')
        
        if not all([staff_id, course_id, semester, class_time]):
            return jsonify({"success": False, "message": "缺少必要参数"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 验证教师和课程是否存在
        cursor.execute("SELECT 1 FROM teacher WHERE staff_id = %s", [staff_id])
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "教师不存在"}), 400
        
        cursor.execute("SELECT 1 FROM course WHERE course_id = %s", [course_id])
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "课程不存在"}), 400
        
        # 检查是否已存在相同的课程安排
        cursor.execute('''
            SELECT 1 FROM class 
            WHERE semester = %s AND course_id = %s AND staff_id = %s
        ''', (semester, course_id, staff_id))
        
        if cursor.fetchone():
            # 更新现有课程安排
            cursor.execute('''
                UPDATE class SET class_time = %s
                WHERE semester = %s AND course_id = %s AND staff_id = %s
            ''', (class_time, semester, course_id, staff_id))
            message = "课程安排已更新"
        else:
            # 添加新的课程安排
            cursor.execute('''
                INSERT INTO class (semester, course_id, staff_id, class_time)
                VALUES (%s, %s, %s, %s)
            ''', (semester, course_id, staff_id, class_time))
            message = "课程已成功分配给教师"
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "message": message})
    except Exception as e:
        return handle_error(e)

@app.route('/api/admin/remove-course', methods=['DELETE'])
def remove_course():
    try:
        data = request.get_json()
        staff_id = data.get('staff_id')
        course_id = data.get('course_id')
        semester = data.get('semester')
        
        if not all([staff_id, course_id, semester]):
            return jsonify({"success": False, "message": "缺少必要参数"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 首先检查该课程是否有学生选课记录
        cursor.execute('''
            SELECT COUNT(*) FROM course_selection
            WHERE staff_id = %s AND course_id = %s AND semester = %s
        ''', (staff_id, course_id, semester))
        
        count = cursor.fetchone()[0]
        if count > 0:
            cursor.close()
            conn.close()
            return jsonify({
                "success": False, 
                "message": f"无法移除课程，该课程已有 {count} 名学生选课"
            }), 400
        
        # 删除课程安排
        cursor.execute('''
            DELETE FROM class
            WHERE semester = %s AND course_id = %s AND staff_id = %s
        ''', (semester, course_id, staff_id))
        
        if cursor.rowcount > 0:
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({"success": True, "message": "课程已成功移除"})
        else:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "未找到该课程安排"}), 404
    except Exception as e:
        return handle_error(e)

@app.route('/api/admin/users', methods=['GET', 'POST'])
def admin_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'GET':
            cursor.execute('''
                SELECT l.*, 
                       COALESCE(s.name, t.name, 'Admin') as name,
                       d.dept_name
                FROM login_info l
                LEFT JOIN student s ON l.user_id = s.user_id
                LEFT JOIN teacher t ON l.user_id = t.user_id
                LEFT JOIN department d ON COALESCE(s.dept_id, t.dept_id) = d.dept_id
            ''')
            users = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify({"success": True, "data": users})
        
        elif request.method == 'POST':
            data = request.get_json()
            
            # Insert into login_info first
            cursor.execute('''
                INSERT INTO login_info (username, password, role)
                VALUES (%s, %s, %s)
            ''', (data['username'], data['password'], data['role']))
            
            user_id = cursor.lastrowid
            
            # Insert into role-specific table
            if data['role'] == 'student':
                cursor.execute('''
                    INSERT INTO student (user_id, student_id, name, dept_id, sex, date_of_birth, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (user_id, data.get('student_id', f'S{user_id}'), data['name'], 
                      data['dept_id'], data.get('sex', 'M'), data.get('date_of_birth', '2000-01-01'), 'active'))
            elif data['role'] == 'teacher':
                cursor.execute('''
                    INSERT INTO teacher (user_id, staff_id, name, dept_id, sex, date_of_birth)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (user_id, data.get('staff_id', f'T{user_id}'), data['name'], 
                      data['dept_id'], data.get('sex', 'M'), data.get('date_of_birth', '1980-01-01')))
            
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({"success": True, "message": "User added successfully"})
            
    except Exception as e:
        return handle_error(e)

# Add stored procedure for grade calculation
@app.route('/api/admin/setup/procedures', methods=['POST'])
def setup_procedures():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Drop procedure if exists
        cursor.execute("DROP PROCEDURE IF EXISTS CalculateFinalGrades")
        
        # Create stored procedure for calculating final grades
        cursor.execute('''
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
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Stored procedures created successfully"})
    except Exception as e:
        return handle_error(e)

# Call stored procedure for grade calculation
@app.route('/api/teacher/calculate-grades', methods=['POST'])
def calculate_grades():
    try:
        data = request.get_json()
        course_id = data.get('course_id')
        semester = data.get('semester')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Call the stored procedure
        args = [course_id, semester]
        cursor.callproc('CalculateFinalGrades', args)
        
        # Get results
        cursor.execute("SELECT s.student_id, s.name, sr.usual_score, sr.final_score, sr.total_score \
                       FROM course_selection cs \
                       JOIN student s ON cs.student_id = s.student_id \
                       JOIN score_record sr ON cs.id = sr.course_selection_id \
                       WHERE cs.course_id = %s AND cs.semester = %s", args)
        results = cursor.fetchall()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Grades calculated successfully",
            "data": results
        })
    except Exception as e:
        return handle_error(e)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
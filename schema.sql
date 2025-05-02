CREATE TABLE login_info (
                            user_id INT NOT NULL AUTO_INCREMENT,      -- 用户ID，INT类型，自增，初始值从100000000开始
                            username VARCHAR(100) NOT NULL,           -- 用户名，不能为空
                            password VARCHAR(255) NOT NULL,           -- 密码，不能为空
                            role ENUM('admin', 'teacher', 'student') NOT NULL,  -- 角色，表示是管理员、教师或学生
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- 创建时间，默认当前时间
                            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 更新时间
                            PRIMARY KEY (user_id),                    -- 设置 user_id 为主键
                            UNIQUE (username)                         -- 用户名唯一
) AUTO_INCREMENT = 100000000;                -- 设置自增起始值为 100000000

CREATE TABLE department (
                            dept_id char(2) NOT NULL,    -- 院系号，主键，自动增长
                            dept_name VARCHAR(100) NOT NULL,        -- 院系名称，字符串，不能为空
                            address VARCHAR(255),                   -- 地址，字符串，可以为空
                            phone_code VARCHAR(15),                 -- 联系电话，字符串，可以为空
                            PRIMARY KEY (dept_id)                   -- 设置主键
);

CREATE TABLE student (
                         student_id char(8) NOT NULL,   -- 学号，主键，自增
                         user_id INT NOT NULL,                     -- 登录信息ID，外键关联 login_info 表
                         name VARCHAR(100) NOT NULL,               -- 姓名
                         sex ENUM('M', 'F') NOT NULL,              -- 性别
                         date_of_birth DATE NOT NULL,              -- 出生日期
                         native_place VARCHAR(100),                -- 籍贯
                         mobile_phone VARCHAR(15),                 -- 手机号码
                         dept_id CHAR(2) NOT NULL,                 -- 院系号
                         status ENUM('active', 'inactive') NOT NULL, -- 状态
                         PRIMARY KEY (student_id),                 -- 设置学号为主键
                         FOREIGN KEY (user_id) REFERENCES login_info(user_id), -- 外键关联 login_info 表
                         FOREIGN KEY (dept_id) REFERENCES department(dept_id) -- 外键关联院系表
);



CREATE TABLE teacher (
                         staff_id char(8) NOT NULL,     -- 工号，主键，自增
                         user_id INT NOT NULL,                     -- 登录信息ID，外键关联 login_info 表
                         name VARCHAR(100) NOT NULL,               -- 姓名
                         sex ENUM('M', 'F') NOT NULL,              -- 性别
                         date_of_birth DATE NOT NULL,              -- 出生日期
                         professional_ranks VARCHAR(100),          -- 职称
                         salary DECIMAL(10, 2),                    -- 基本工资
                         dept_id CHAR(2) NOT NULL,                 -- 院系号
                         PRIMARY KEY (staff_id),                   -- 设置工号为主键
                         FOREIGN KEY (user_id) REFERENCES login_info(user_id), -- 外键关联 login_info 表
                         FOREIGN KEY (dept_id) REFERENCES department(dept_id) -- 外键关联院系表
);


CREATE TABLE course (
                        course_id char(8) NOT NULL,       -- 课号，主键，自动增长
                        course_name VARCHAR(100) NOT NULL,           -- 课程名称，字符串，不能为空
                        credit INT DEFAULT 4,                        -- 学分，整数，默认为 4
                        credit_hours INT DEFAULT 40,                 -- 学时，整数，默认为 40
                        dept_id char(2) NOT NULL,                        -- 院系号，整数，不能为空
                        PRIMARY KEY (course_id),                     -- 设置课号为主键
                        FOREIGN KEY (dept_id) REFERENCES department(dept_id) -- 外键，指向院系表 department 的 dept_id
);

CREATE TABLE class (
                       semester VARCHAR(20) NOT NULL,              -- 学期，字符串类型，不能为空
                       course_id char(8) NOT NULL,                     -- 课号，整数，不能为空
                       staff_id char(8) NOT NULL,                      -- 工号，整数，不能为空
                       class_time DATETIME NOT NULL,               -- 上课时间，日期时间类型，不能为空
                       PRIMARY KEY (semester, course_id, staff_id), -- 联合主键，由学期、课号和工号组成
                       FOREIGN KEY (course_id) REFERENCES course(course_id),  -- 外键，指向课程表 course 的 course_id
                       FOREIGN KEY (staff_id) REFERENCES teacher(staff_id)    -- 外键，指向教师表 teacher 的 staff_id
);

CREATE TABLE course_selection (
                                  id INT AUTO_INCREMENT PRIMARY KEY,           -- 单独的主键
                                  student_id char(8) NOT NULL,                     -- 学号，外键
                                  semester VARCHAR(20) NOT NULL,               -- 学期
                                  course_id char(8) NOT NULL,                      -- 课程ID，外键
                                  staff_id char(8) NOT NULL,                       -- 工号，外键
                                  score INT CHECK (score >= 1 AND score <= 100), -- 成绩，整数，范围为 1 到 100，不能为空
                                  FOREIGN KEY (student_id) REFERENCES student(student_id), -- 外键，关联学生表
                                  FOREIGN KEY (course_id) REFERENCES course(course_id),    -- 外键，关联课程表
                                  FOREIGN KEY (staff_id) REFERENCES teacher(staff_id),      -- 外键，关联教师表
    -- 添加唯一约束，防止 student_id, semester, course_id 组合重复
                                  UNIQUE (student_id, semester, course_id)
);




CREATE INDEX idx1 ON student (dept_id ASC, name DESC);
CREATE INDEX idx2 ON course (course_name);




CREATE TABLE admin (
                       admin_id INT NOT NULL AUTO_INCREMENT,     -- 管理员ID，主键，自增
                       user_id INT NOT NULL,                     -- 登录信息ID，外键关联 login_info 表
                       role ENUM('superadmin', 'admin') NOT NULL, -- 角色，'superadmin' 超级管理员，'admin' 普通管理员
                       created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
                       updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 更新时间
                       PRIMARY KEY (admin_id),                   -- 设置管理员ID为主键
                       FOREIGN KEY (user_id) REFERENCES login_info(user_id) -- 外键关联 login_info 表
);

CREATE TABLE user_activity_log (
                                   log_id INT AUTO_INCREMENT PRIMARY KEY,         -- 日志ID，主键
                                   user_id INT NOT NULL,                          -- 用户ID
                                   action VARCHAR(100) NOT NULL,                  -- 用户执行的操作
                                   action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 操作时间
                                   ip_address VARCHAR(50),                         -- 用户操作时的IP地址
                                   FOREIGN KEY (user_id) REFERENCES login_info(user_id)
);




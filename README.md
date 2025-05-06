# 数据库初始化脚本

本目录包含用于初始化课程选择系统数据库的脚本。

## 脚本说明

- `init_test_users.py`: 仅初始化基本用户账户和少量测试数据
- `init_full_database.py`: 完整初始化整个数据库，包括所有表结构和丰富的测试数据

## 使用方法

### 完整初始化数据库

```bash
python init_full_database.py
```

此脚本将：
1. 删除现有数据库（如果存在）
2. 创建新的数据库
3. 创建所有表结构（login_info, department, admin, student, teacher, course, class, course_selection, score_record, homework_log, quiz_log, user_activity_log）
4. 添加丰富的测试数据，包括：
   - 5个院系
   - 2个管理员账户
   - 5个教师账户
   - 10个学生账户
   - 13门课程
   - 当前学期和上一学期的课程安排
   - 学生选课记录
   - 上一学期课程的成绩记录
   - 作业和测验记录
   - 用户活动日志记录

### 仅初始化测试用户

```bash
python init_test_users.py
```

此脚本仅初始化基本用户和测试数据，适合开发环境快速测试使用。

## 测试用户账户

### 管理员
- 用户名: admin, 密码: admin123
- 用户名: superadmin, 密码: super123

### 教师
- 用户名: teacher1-teacher5, 密码: teacher123

### 学生
- 用户名: student1-student10, 密码: student123

## 数据库配置

脚本中的数据库配置如下：

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'course_selection_system'
}
```

如需修改数据库连接参数，请编辑脚本中的DB_CONFIG变量。 
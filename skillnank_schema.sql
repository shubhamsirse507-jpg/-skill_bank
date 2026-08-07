CREATE DATABASE skillbank;
USE skillbank;

CREATE TABLE roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    role_id INT,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL
);

CREATE TABLE skills (
    skill_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL,
    category_id INT NOT NULL,
    skill_name VARCHAR(100) NOT NULL,
    description TEXT,
    FOREIGN KEY (teacher_id) REFERENCES users(user_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL,
    category_id INT NOT NULL,
    course_name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2),
    duration VARCHAR(50),
    FOREIGN KEY (teacher_id) REFERENCES users(user_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
); 

CREATE TABLE enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    enrollment_date DATE,
    status ENUM('Enrolled','Completed','Cancelled') DEFAULT 'Enrolled',
    FOREIGN KEY (student_id) REFERENCES users(user_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

CREATE TABLE learning_progress (
    progress_id INT AUTO_INCREMENT PRIMARY KEY,
    enrollment_id INT NOT NULL,
    progress_percent INT DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id)
);

CREATE TABLE doubts (
    doubt_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    teacher_id INT NOT NULL,
    course_id INT NOT NULL,
    doubt_title VARCHAR(150) NOT NULL,
    doubt_description TEXT NOT NULL,
    status ENUM('Open','Resolved','Closed') DEFAULT 'Open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(user_id),
    FOREIGN KEY (teacher_id) REFERENCES users(user_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

CREATE TABLE chat_messages (
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    doubt_id INT NOT NULL,
    sender_id INT NOT NULL,
    message TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doubt_id) REFERENCES doubts(doubt_id),
    FOREIGN KEY (sender_id) REFERENCES users(user_id)
);

CREATE TABLE sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL,
    session_title VARCHAR(100) NOT NULL,
    session_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    meeting_link VARCHAR(255),
    status ENUM('Scheduled','Completed','Cancelled') DEFAULT 'Scheduled',
    FOREIGN KEY (teacher_id) REFERENCES users(user_id)
);

CREATE TABLE bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    student_id INT NOT NULL,
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    booking_status ENUM('Pending','Confirmed','Cancelled','Completed') DEFAULT 'Pending',
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    FOREIGN KEY (student_id) REFERENCES users(user_id)
);

CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    booking_id INT,
    course_id INT,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50),
    payment_status ENUM('Pending','Paid','Failed') DEFAULT 'Pending',
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(user_id),
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id),
    FOREIGN KEY (course_id) REFERENCES  courses(course_id)
);

CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    payment_id INT NOT NULL,
    transaction_reference VARCHAR(100) UNIQUE,
    transaction_status ENUM('Success','Failed','Pending') DEFAULT 'Pending',
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (payment_id) REFERENCES payments(payment_id)
);

CREATE TABLE invoices (
    invoice_id INT AUTO_INCREMENT PRIMARY KEY,
    payment_id INT NOT NULL,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    invoice_date DATE NOT NULL,
    FOREIGN KEY (payment_id) REFERENCES payments(payment_id)
);

CREATE TABLE earnings (
    earning_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL,
    payment_id INT NOT NULL,
    total_earning DECIMAL(10,2) NOT NULL,
    platform_commission DECIMAL(10,2) NOT NULL,
    teacher_earning DECIMAL(10,2) NOT NULL,
    earning_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES users(user_id),
    FOREIGN KEY (payment_id) REFERENCES payments(payment_id)
);

CREATE TABLE withdrawals (
    withdrawal_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Pending','Approved','Rejected') DEFAULT 'Pending',
    FOREIGN KEY (teacher_id) REFERENCES users(user_id)
);

CREATE TABLE feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    teacher_id INT NOT NULL,
    course_id INT NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    review TEXT,
    feedback_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(user_id),
    FOREIGN KEY (teacher_id) REFERENCES users(user_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    notification_type ENUM('Booking','Payment','Course','Session','General') DEFAULT 'General',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE otp_verification (
    otp_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    otp_code VARCHAR(10) NOT NULL,
    purpose ENUM('Registration','Login','ForgotPassword') NOT NULL,
    expires_at DATETIME NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
CREATE TABLE doubt_files (
    file_id INT AUTO_INCREMENT PRIMARY KEY,
    doubt_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doubt_id) REFERENCES doubts(doubt_id)
);



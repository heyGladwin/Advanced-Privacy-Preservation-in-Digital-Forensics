CREATE DATABASE IF NOT EXIST forencyrpt;

USE forencrypt;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,

    username VARCHAR(100) NOT NULL UNIQUE,

    email VARCHAR(150) NOT NULL UNIQUE,

    password_hash VARCHAR(255) NOT NULL,

    role ENUM('admin', 'investigator')
        DEFAULT 'investigator',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
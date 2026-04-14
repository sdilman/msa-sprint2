DROP TABLE IF EXISTS review;
DROP TABLE IF EXISTS booking;
DROP TABLE IF EXISTS promo_code;
DROP TABLE IF EXISTS hotel;
DROP TABLE IF EXISTS app_user;

CREATE TABLE app_user (
    id VARCHAR(255) PRIMARY KEY,
    status VARCHAR(50),
    blacklisted BOOLEAN,
    active BOOLEAN,
    name VARCHAR(255),
    email VARCHAR(255),
    city VARCHAR(255)
);

CREATE TABLE hotel (
    id VARCHAR(255) PRIMARY KEY,
    operational BOOLEAN,
    fully_booked BOOLEAN,
    city VARCHAR(255),
    rating DOUBLE PRECISION,
    description TEXT
);

CREATE TABLE review (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    hotel_id VARCHAR(255),
    text TEXT,
    rating INTEGER,
    created_at DATE
);

CREATE TABLE promo_code (
    code VARCHAR(255) PRIMARY KEY,
    discount DOUBLE PRECISION,
    vip_only BOOLEAN,
    expired BOOLEAN,
    valid_until DATE,
    description TEXT
);

CREATE TABLE booking (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    hotel_id VARCHAR(255),
    promo_code VARCHAR(255),
    discount_percent DOUBLE PRECISION,
    price DOUBLE PRECISION,
    created_at TIMESTAMP
);

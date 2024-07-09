CREATE TABLE IF NOT EXISTS users (
    user_uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_fname VARCHAR(255) NOT NULL,
    user_lname VARCHAR(255) NOT NULL,
    user_password VARCHAR(255) NOT NULL,
    user_email VARCHAR(255) UNIQUE NOT NULL,
    user_role VARCHAR(255) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS requests (
    request_uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_status VARCHAR(255) NOT NULL DEFAULT 'TO BE REVIEWED',
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    user_uuid UUID NOT NULL,
    CONSTRAINT fk_user_uuid
        FOREIGN KEY(user_uuid)
            REFERENCES users(user_uuid)
                ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS appointments (
    appointment_uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    appointment_date TIMESTAMP NOT NULL,
    user_uuid UUID NOT NULL,
    request_uuid UUID NOT NULL,
    CONSTRAINT fk_user_uuid
        FOREIGN KEY(user_uuid)
            REFERENCES users(user_uuid)
                ON DELETE CASCADE,
    CONSTRAINT fk_request_uuid
        FOREIGN KEY(request_uuid)
            REFERENCES requests(request_uuid)
                ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS records (
    record_uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    record_content TEXT NOT NULL,
    user_uuid UUID NOT NULL,
    appointment_uuid UUID NOT NULL,
    CONSTRAINT fk_user_uuid
        FOREIGN KEY(user_uuid)
            REFERENCES users(user_uuid)
                ON DELETE CASCADE,
    CONSTRAINT fk_appointment_uuid
        FOREIGN KEY(appointment_uuid)
            REFERENCES appointments(appointment_uuid)
                ON DELETE CASCADE
);
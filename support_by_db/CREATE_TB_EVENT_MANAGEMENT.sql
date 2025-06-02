CREATE TABLE events_mange(
	event_id INT AUTO_INCREMENT PRIMARY KEY,
	user_id BIGINT,
    user_message VARCHAR(255),
    admin_id BIGINT,
    admin_answer VARCHAR(255),
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (admin_id) REFERENCES admins(admin_id)
)
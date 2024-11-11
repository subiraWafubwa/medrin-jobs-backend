# Medrin Jobs Backend

This repository contains the backend code of Medrin Jobs project using Flask (python).

## User journey and Routes

In this sesction, I have added the route data according to the user's journey e.g. the step-by_step processes in which a user creates an account.

### Authentication(SignUp, Login and Logout) Journey

| Route               | CRUD Operation    | Description                                                                                                                                                                                                           | Models Involved | Data Manipulated                                                    |
| ------------------- | ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ------------------------------------------------------------------- |
| `/register`         | Create            | Registers a new user by accepting email, password and role. Generates and sends an OTP to the user's email. Note that `otp` is saved as session data. Not in the database.                                            | User, RoleEnum  | `email`, `password`, `role`, `otp`                                  |
| `/verify_otp`       | Create            | Verifies the OTP and creates a new user account upon successful OTP validation. A JWT token us also generated. The appropriate route (`/create_employer` or `/create_jobseeker`) should then be chosen appropriately. | User, RoleEnum  | `email`, `otp_input`, `password`, `role`, `access_token`, `user_id` |
| `/create_jobseeker` | Create            | Creates a JobSeeker profile after the user has been registered and OTP has been verified.                                                                                                                             | JobSeeker, User | `first_name`, `last_name`, `location`, `phone`, `dob`, `user_id`    |
| `/create_employer`  | Create            | Creates an Employer profile after the user has been registered and OTP has been verified.                                                                                                                             | Employer, User  | `name`, `location`, `description`, `mission`, `vision`, `user_id`   |
| `/login`            | Read/Authenticate | Authenticates a user by validating the email and password. If valid, generates and returns a JWT token. Wrapped with `token_required()` from `auth.py`                                                                | User            | `email`, `password`, `access_token`                                 |
| `/logout`           | Logout            | Logs out a user by revoking the JWT token and clearing session data. Wrapped with `check_if_token_in_blacklist` from `auth.py`                                                                                        | User, JWT       | `access_token`, `jti` (JWT unique identifier)                       |

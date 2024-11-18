# Medrin Jobs Backend

This repository contains the backend code of Medrin Jobs project using Flask (python).

## User journey

| User      | Description                                                                                                                                                                                                                                                                                                                                                                                                                             | Models Associated                                                                                                                                                                                                                                           |
| --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Employer  | 1. Create user account and Employer profile data <br> 2. Can view and update his profile data. <br> 3. Post a new job <br> 4. Get list of jobs posted. <br> 4. View applicants for a particular jobs. <br> 5. View applicants profile. <br> 6. Approving and rejecting applications. <br> 7. Sending email notifications to users for application status. <br> 8. Shortlisting applications for each job. <br> 9. Purchasing job slots. | 1. `User`, `Employer` <br> 2. `Employer` <br> 3. `Job`, `JobResponsibility`, `JobRequirements` <br> 4. `Jobs` <br> 5. `Applications` <br> 6. `Applications` <br> 7. `No model associated` <br> 8. `shortlisted_applications` <br> 9. `Payments`, `Employer` |
| Jobseeker | 1. View all jobs available for application. <br> 2. Apply for a particular job. <br> 3. Create user account and Jobseeker profile data. <br> 4. Update profile data. <br> 5. View job applications. <br> 6. View her applications' status. <br>                                                                                                                                                                                         | 1. `Jobs`, `shortlisted_applications` <br> 2. `Jobs` <br> 3. `Jobseeker`, `User` <br> 4. `Jobseeker` <br> 5. `Applications` <br> 6. `Applications`                                                                                                          |

## Routes

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

### Job Application Routes

| Route        | CRUD Operation | Description                                                                                                                                                                                                                                                                                           | Models Involved                   | Data Manipulated              |
| ------------ | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- | ----------------------------- |
| `/apply-job` | POST           | **Input:** JSON data containing `job_id` and `jobseeker_id`. Validates `job_id` and `jobseeker_id` as UUIDs. <br> **Process:** Checks if the job and job seeker exist. <br> **Output:** Creates an `Application` record with `job_id`, `jobseeker_id`, a `pending` status, and the current timestamp. | `Application`, `JobSeeker`, `Job` | Posting a new job application |

### Job Routes

| Route                                   | CRUD Operation | Description                                    | Models Involved            | Data Manipulated                                                                                                                                                                                                                                                  |
| --------------------------------------- | -------------- | ---------------------------------------------- | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/add_job/<uuid:employer_id>`           | POST           | Adds a new job for a specific employer         | `Job`, `Employer`          | **Input:** `title`, `description`, `industry`, `level`, `job_type`. Validates the existence of the `employer` and checks if required fields and enums are correct. <br> **Output:** Creates a new `Job` record with the current timestamp and job details.        |
| `/add_job_requirements/<uuid:job_id>`   | POST           | Adds or updates job requirements for a job     | `JobRequirement`, `Job`    | **Input:** JSON containing `requirements`. Validates the existence of the `job`. <br> **Process:** Deletes any existing requirements for the job and creates new ones. <br> **Output:** Creates a `JobRequirement` record linked to the specified `job_id`.       |
| `/add_job_responsibility/<uuid:job_id>` | POST           | Adds or updates job responsibilities for a job | `JobResponsibility`, `Job` | **Input:** JSON containing `description`. Validates the existence of the `job`. <br> **Process:** Deletes any existing responsibilities for the job and creates new ones. <br> **Output:** Creates a `JobResponsibility` record linked to the specified `job_id`. |

### User Routes

| Route          | CRUD Operation | Description                                       | Models Involved | Data Manipulated                                                                                                                                      |
| -------------- | -------------- | ------------------------------------------------- | --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/get_profile` | GET            | Fetches user profile data for authenticated users | `User`          | **Input:** None (requires authentication via token). <br> **Output:** Returns a JSON object with the user's `id`, `email`, `role`, and `employer_id`. |

## Payment Plans

### Organisation Model

- `job_post_slots` tracks the number of posts allowed.

- `plan_expiry` tracks expiration dates for premium plans.

- The `update_plan` method manages plan changes, updates expiry for premium, and sets custom slots for pro-rated. It has been set to handle monthly and yearly premium plans. Pro-rated plans handles

### Plan Model

- Contains job_post_limit to define limits for pro-rated plans or premium if they have caps.
- Defines duration to represent if it’s monthly, yearly, or per-job.

### Payment Model

- Tracks the type and amount of payment.

- Links each payment to a plan and organization.

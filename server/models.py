from sqlalchemy import Column, String, Table, Text, DateTime, Enum, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
import uuid
from config import db
import enum

# Main user models
class RoleEnum(enum.Enum):
    admin = "admin"
    job_seeker = "job_seeker"
    employer = "employer"

class User(db.Model, SerializerMixin):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(Enum(RoleEnum), nullable=False)

    jobseeker = relationship("JobSeeker", uselist=False, back_populates="user")
    employer = relationship("Employer", uselist=False, back_populates="user")

# Employer stories: CRUD jobs, make payments and shortlist applications
class Employer(db.Model, SerializerMixin):
    __tablename__ = "employers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String)
    location = Column(String)
    description = Column(String)
    mission = Column(String)
    vision = Column(String)

    user = relationship("User", back_populates="employer")
    jobs = relationship("Job", back_populates="employer")
    payment = relationship("Payment", back_populates="employer")
    serialize_rules = ("-user.employer", "-payment.employer", "-jobs.employer")

class JobTypeEnum(enum.Enum):
    freelance = "freelance"
    fulltime = "full_time"
    parttime = "part_time"
    internship = "internship"

class JobLevelEnum(enum.Enum):
    entry_level = "entry_level"
    mid_level = "mid_level"
    senior_level = "senior_level"

class IndustryEnum(enum.Enum):
    telcos = "telcos"
    software = "software"

# Association table for short-listed applications
shortlisted_applications = Table(
    'shortlisted_applications',
    db.Model.metadata,
    Column('job_id', UUID(as_uuid=True), ForeignKey('jobs.id'), primary_key=True),
    Column('application_id', UUID(as_uuid=True), ForeignKey('applications.jobseeker_id'), primary_key=True),
)

class Job(db.Model, SerializerMixin):
    __tablename__ = "jobs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employer_id = Column(UUID(as_uuid=True), ForeignKey("employers.id"))
    industry = Column(Enum(IndustryEnum))
    title = Column(String)
    description = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    level = Column(Enum(JobLevelEnum))
    job_type = Column(Enum(JobTypeEnum))
    date_posted = Column(DateTime)

    job_responsibilities = relationship("JobResponsibility", back_populates="job")
    job_requirements = relationship("JobRequirement", back_populates="job")
    employer = relationship("Employer", back_populates="jobs")
    shortlisted_applications = relationship(
        "Application",
        secondary=shortlisted_applications,
        back_populates="shortlisted_jobs",
        primaryjoin=id == shortlisted_applications.c.job_id,
        secondaryjoin="Application.jobseeker_id == shortlisted_applications.c.application_id"
    )
    serialize_rules = ("-job_responsibilities.job", "-job_requirements.job",)

class JobRequirement(db.Model, SerializerMixin):
    __tablename__ = "job_requirements"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"))
    requirements = Column(Text)

    job = relationship("Job", back_populates="job_requirements")
    serialize_rules = ("-job.job_requirements",)

class JobResponsibility(db.Model, SerializerMixin):
    __tablename__ = "job_responsibilities"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(Text)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"))

    job = relationship("Job", back_populates="job_responsibilities")
    serialize_rules = ("-job.job_responsibilities",)

class PaymentTypeEnum(enum.Enum):
    mpesa = "mpesa"
    bank = "bank"

class Payment(db.Model, SerializerMixin):
    __tablename__ = "payments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employer_id = Column(UUID(as_uuid=True), ForeignKey("employers.id"))
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"))
    payment_type = Column(Enum(PaymentTypeEnum))

    plan = relationship("Plan", back_populates="payment")
    employer = relationship("Employer", back_populates="payment")
    serialize_rules = ("-plan.payment", "-employer.payment",)

class PlanEnum(enum.Enum):
    freemium = "freemium"
    premium = "premium"
    pro_rated = "pro_rated"

class Plan(db.Model, SerializerMixin):
    __tablename__ = "plans"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Enum(PlanEnum))
    price = Column(DECIMAL)

    payment = relationship("Payment", back_populates="plan")
    serialize_rules = ("-payments.plan",)

# Jobseeker stories: Applying for jobs, Editing data including education and experience
class JobSeeker(db.Model, SerializerMixin):
    __tablename__ = "jobseekers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True,  nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    location = Column(String)
    phone = Column(String)
    dob = Column(DateTime)

    user = relationship("User", back_populates="jobseeker")
    applications = relationship("Application", back_populates="jobseeker")
    educations = relationship("Education", back_populates="jobseeker", cascade="all, delete-orphan")
    experiences = relationship("Experience", back_populates="jobseeker", cascade="all, delete-orphan")
    serialize_rules = ("-user.jobseeker", "-applications.jobseeker","-educations.jobseeker", "-experiences.jobseeker")

class EducationLevelEnum(enum.Enum):
    certificate = "certificate"
    diploma = "diploma"
    degree = "degree"
    masters = "masters"
    phd = "phd"

class Education(db.Model, SerializerMixin):
    __tablename__ = "educations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    jobseeker_id = Column(UUID(as_uuid=True), ForeignKey("jobseekers.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    institution = Column(String)
    qualification = Column(String)
    course = Column(String)
    level = Column(Enum(EducationLevelEnum))

    jobseeker = relationship("JobSeeker", back_populates="educations")
    serialize_rules = ("-jobseeker.educations",)

class Experience(db.Model, SerializerMixin):
    __tablename__ = "experiences"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    jobseeker_id = Column(UUID(as_uuid=True), ForeignKey("jobseekers.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    description = Column(Text)
    employer = Column(String)
    job_title = Column(String)

    jobseeker = relationship("JobSeeker", back_populates="experiences")
    serialize_rules = ("-jobseeker.experiences",)

class ApplicationStatusEnum(enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class Application(db.Model, SerializerMixin):
    __tablename__ = "applications"
    __table_args__ = (
        db.PrimaryKeyConstraint('jobseeker_id', 'job_id'),
    )

    jobseeker_id = Column(UUID(as_uuid=True), ForeignKey("jobseekers.id"))
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"))
    created_at = Column(DateTime)
    status = Column(Enum(ApplicationStatusEnum), default=ApplicationStatusEnum.pending)

    jobseeker = relationship("JobSeeker", back_populates="applications")
    shortlisted_jobs = relationship(
        "Job", 
        secondary=shortlisted_applications, 
        back_populates="shortlisted_applications",
        primaryjoin=jobseeker_id == shortlisted_applications.c.application_id,
        secondaryjoin=job_id == shortlisted_applications.c.job_id
    )
    serialize_rules = ("-jobseeker.applications",)
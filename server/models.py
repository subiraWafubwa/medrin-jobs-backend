from datetime import datetime, timedelta
from sqlalchemy import Column, Date, String, Table, Text, DateTime, Enum, ForeignKey, DECIMAL, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
import uuid
from config import db
import enum

# Enums
class RoleEnum(enum.Enum):
    job_seeker = "job_seeker"
    organisation = "organisation"
    recruiter = "recruiter"

class PlanEnum(enum.Enum):
    free = "free"
    premium = "premium"
    pro_rated = "pro_rated"

class PaymentTypeEnum(enum.Enum):
    mpesa = "mpesa"
    bank = "bank"

class JobTypeEnum(enum.Enum):
    freelance = "freelance"
    full_time = "full_time"
    part_time = "part_time"

class JobLevelEnum(enum.Enum):
    internship = "internship"
    entry_level = "entry_level"
    mid_level = "mid_level"
    senior_level = "senior_level"

class IndustryEnum(enum.Enum):
    agriculture = "agriculture"
    banking_finance = "banking_finance"
    building_construction = "building_construction"
    business = "business"
    customer_service = "customer_service"
    government = "government"
    healthcare = "healthcare"
    hospitality = "hospitality"
    human_resource = "human_resource"
    it_software = "it_software"
    legal = "legal"
    marketing_communication = "marketing_communication"
    project_management = "project_management"
    teaching = "teaching"

class EducationLevelEnum(enum.Enum):
    certificate = "certificate"
    diploma = "diploma"
    degree = "degree"
    masters = "masters"
    phd = "phd"

class ApplicationStatusEnum(enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

# Association table for short-listed applications
shortlisted_applications = Table(
    'shortlisted_applications',
    db.Model.metadata,
    Column('job_id', UUID(as_uuid=True), ForeignKey('jobs.id'), primary_key=True),
    Column('application_id', UUID(as_uuid=True), ForeignKey('applications.id'), primary_key=True),  # Assuming Application has an 'id'
)

# Main user models
class User(db.Model, SerializerMixin):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(Enum(RoleEnum), nullable=False)
    timestamp = Column(DateTime, default=datetime.now)

    jobseeker = relationship("JobSeeker", uselist=False, back_populates="user")
    organisation = relationship("Organisation", uselist=False, back_populates="user")
    recruiter = relationship("Recruiter", uselist=False, back_populates="user")
    blacklisted_tokens = relationship("BlacklistedToken", back_populates="user")

    serialize_rules = ("-jobseeker.user", "-organisation.user", "-recruiter.user",)

class BlacklistedToken(db.Model):
    __tablename__ = "blacklisted_tokens"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token = Column(Text)
    user = relationship("User", back_populates="blacklisted_tokens")

    serialize_rules = ("-user.blacklisted_tokens")

class Recruiter(db.Model, SerializerMixin):
    __tablename__ = "recruiters"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True, nullable=False)
    organisation_id = Column(UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False)
    email = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    dob = Column(Date)
    
    organisation = relationship("Organisation", back_populates="recruiters")
    user = relationship("User", back_populates="recruiter")
    
    serialize_rules = ("-organisation.recruiters", "-user.recruiter",)

# Organisation models
class Organisation(db.Model, SerializerMixin):
    __tablename__ = "organisations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    logo = Column(Text, nullable=True)
    name = Column(String, nullable=False)
    location = Column(String)
    description = Column(String)
    mission = Column(String)
    vision = Column(String)
    
    plan = Column(Enum(PlanEnum), default=PlanEnum.free)
    job_post_slots = Column(Integer, default=3)  # Free plan gets 3 initial slots
    plan_expiry = Column(DateTime, nullable=True)  # Tracks expiration for premium plans
    
    user = relationship("User", back_populates="organisation")
    recruiters = relationship("Recruiter", back_populates="organisation")
    jobs = relationship("Job", back_populates="organisation")
    payments = relationship("Payment", back_populates="organisation")
    
    serialize_rules = ("-user.organisation", "-payments.organisation", "-jobs.organisation",)

    def update_plan(self, new_plan, duration=None, slots=None):
        self.plan = new_plan
        if new_plan == PlanEnum.premium and duration:
            self.plan_expiry = datetime.now() + timedelta(days=30 if duration == 'monthly' else 365)
            self.job_post_slots = None
        elif new_plan == PlanEnum.pro_rated:
            self.job_post_slots = slots or 10
            self.plan_expiry = None

class Plan(db.Model, SerializerMixin):
    __tablename__ = "plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Enum(PlanEnum), nullable=False)
    description = Column(String)
    job_post_limit = Column(Integer, nullable=True)  # e.g., "per_job" for pro-rated
    duration = Column(String)  # E.g., "monthly" or "yearly" 
    
    payments = relationship("Payment", back_populates="plan")
    
    serialize_rules = ("-payments.plan",)

class Payment(db.Model, SerializerMixin):
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organisation_id = Column(UUID(as_uuid=True), ForeignKey("organisations.id"))
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"))
    payment_type = Column(Enum(PaymentTypeEnum), nullable=False)
    amount = Column(Integer)  # Amount paid
    
    plan = relationship("Plan", back_populates="payments")
    organisation = relationship("Organisation", back_populates="payments")
    
    serialize_rules = ("-plan.payments", "-organisation.payments",)

# Job models
class Job(db.Model, SerializerMixin):
    __tablename__ = "jobs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organisation_id = Column(UUID(as_uuid=True), ForeignKey("organisations.id"))
    industry = Column(Enum(IndustryEnum))
    title = Column(String)
    description = Column(Text)
    timestamp = Column(DateTime, default=datetime.now)
    level = Column(Enum(JobLevelEnum))
    job_type = Column(Enum(JobTypeEnum))

    job_responsibilities = relationship("JobResponsibility", back_populates="job", cascade="all, delete-orphan")
    job_requirements = relationship("JobRequirement", back_populates="job", cascade="all, delete-orphan")
    job_benefits = relationship("JobBenefits", back_populates="job", cascade="all, delete-orphan")
    organisation = relationship("Organisation", back_populates="jobs")
    shortlisted_applications = relationship(
        "Application",
        secondary=shortlisted_applications,
        back_populates="shortlisted_jobs",
        primaryjoin=id == shortlisted_applications.c.job_id,
        secondaryjoin="Application.id == shortlisted_applications.c.application_id"
    )
    serialize_rules = ("-job_responsibilities.job", "-job_requirements.job", "-job_benefits.job")

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
    responsibilities = Column(Text)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"))

    job = relationship("Job", back_populates="job_responsibilities")
    serialize_rules = ("-job.job_responsibilities",)

class JobBenefits(db.Model, SerializerMixin):
    __tablename__ = "job_benefits"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    benefits = Column(Text)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"))

    job = relationship("Job", back_populates="job_benefits")
    serialize_rules = ("-job.job_benefits",)

# JobSeeker models
class JobSeeker(db.Model, SerializerMixin):
    __tablename__ = "jobseekers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True,  nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    location = Column(String)
    phone = Column(String)
    dob = Column(Date)
    cv = Column(Text, nullable=True)

    user = relationship("User", back_populates="jobseeker")
    applications = relationship("Application", back_populates="jobseeker")
    educations = relationship("Education", back_populates="jobseeker", cascade="all, delete-orphan")
    experiences = relationship("Experience", back_populates="jobseeker", cascade="all, delete-orphan")
    serialize_rules = ("-user.jobseeker", "-applications.jobseeker","-educations.jobseeker", "-experiences.jobseeker")

class Education(db.Model, SerializerMixin):
    __tablename__ = "educations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    jobseeker_id = Column(UUID(as_uuid=True), ForeignKey("jobseekers.id"))
    start_date = Column(Date)
    end_date = Column(Date)
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
    organisation = Column(String)
    job_title = Column(String)

    jobseeker = relationship("JobSeeker", back_populates="experiences")
    serialize_rules = ("-jobseeker.experiences",)

# Application models
class Application(db.Model, SerializerMixin):
    __tablename__ = "applications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # New primary key
    jobseeker_id = Column(UUID(as_uuid=True), ForeignKey("jobseekers.id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    status = Column(Enum(ApplicationStatusEnum), default=ApplicationStatusEnum.pending)

    jobseeker = relationship("JobSeeker", back_populates="applications")
    shortlisted_jobs = relationship(
        "Job", 
        secondary=shortlisted_applications, 
        back_populates="shortlisted_applications",
        primaryjoin=id == shortlisted_applications.c.application_id,  # Updated join condition
        secondaryjoin="Job.id == shortlisted_applications.c.job_id"
    )
    serialize_rules = ("-jobseeker.applications",)


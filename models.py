from sqlalchemy import Column, String, Text, Integer, Float, DateTime, Enum, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from config import db
import enum


# Enums
class PaymentTypeEnum(enum.Enum):
    mpesa = "mpesa"
    bank = "bank"

class PlanEnum(enum.Enum):
    freemium = "freemium"
    premium = "premium"
    pro_rated = "pro_rated"

class IndustryEnum(enum.Enum):
    telcos = "telcos"
    software = "software"

class JobTypeEnum(enum.Enum):
    freelance = "freelance"
    fulltime = "fulltime"
    parttime = "parttime"
    internship = "internship"

class JobLevelEnum(enum.Enum):
    entry_level = "entry_level"
    mid_level = "mid_level"
    senior_level = "senior_level"

class RoleEnum(enum.Enum):
    admin = "admin"
    job_seeker = "job_seeker"
    employer = "employer"

class ApplicationStatusEnum(enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class EducationLevelEnum(enum.Enum):
    certificate = "certificate"
    diploma = "diploma"
    degree = "degree"
    masters = "masters"
    phd = "phd"


# Models
class Company(db.Model):
    __tablename__ = "company"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    location = Column(String)
    description = Column(String)
    mission = Column(String)
    vision = Column(String)

    industries = relationship("IndustryCompany", back_populates="company")
    payments = relationship("Payment", back_populates="company")

    serialize_rules = ("-industries.company", "-payments.company",)

class Plan(db.Model):
    __tablename__ = "plans"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Enum(PlanEnum))
    price = Column(DECIMAL)

    payments = relationship("Payment", back_populates="plan")

    serialize_rules = ("-payments.plan",)

class Payment(db.Model):
    __tablename__ = "payments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_type = Column(Enum(PaymentTypeEnum))
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"))
    company_id = Column(UUID(as_uuid=True), ForeignKey("company.id"))

    plan = relationship("Plan", back_populates="payments")
    company = relationship("Company", back_populates="payments")

    serialize_rules = ("-plan.payments", "-company.payments",)

class IndustryCompany(db.Model):
    __tablename__ = "industry_company"
    company_id = Column(UUID(as_uuid=True), ForeignKey("company.id"), primary_key=True)
    industry = Column(UUID(as_uuid=True), ForeignKey("industry.id"), primary_key=True)

class Industry(db.Model):
    __tablename__ = "industry"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Enum(IndustryEnum))

class Job(db.Model):
    __tablename__ = "job"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String)
    description = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    level = Column(Enum(JobLevelEnum))
    job_type = Column(Enum(JobTypeEnum))
    date_posted = Column(DateTime)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company.id"))

    responsibilities = relationship("JobResponsibility", back_populates="job")
    requirements = relationship("Requirement", back_populates="job")

    serialize_rules = ("-responsibilities.job", "-requirements.job",)

class Tag(db.Model):
    __tablename__ = "tags"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)

class UserTag(db.Model):
    __tablename__ = "user_tags"
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id"), primary_key=True)


class JobTag(db.Model):
    __tablename__ = "job_tags"
    job_id = Column(UUID(as_uuid=True), ForeignKey("job.id"), primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id"), primary_key=True)


class JobResponsibility(db.Model):
    __tablename__ = "job_responsibilities"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(Text)
    job_id = Column(UUID(as_uuid=True), ForeignKey("job.id"))

    job = relationship("Job", back_populates="responsibilities")

    serialize_rules = ("-job.responsibilities",)


class Requirement(db.Model):
    __tablename__ = "requirements"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(Text)
    job_id = Column(UUID(as_uuid=True), ForeignKey("job.id"))

    job = relationship("Job", back_populates="requirements")

    serialize_rules = ("-job.requirements",)


class User(db.Model):
    __tablename__ = "user"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True)
    password = Column(String)
    code = Column(String)

    profile = relationship("Profile", uselist=False, back_populates="user")
    applications = relationship("Application", back_populates="user")

    serialize_rules = ("-profile.user", "-applications.user",)


class Profile(db.Model):
    __tablename__ = "profile"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String)
    last_name = Column(String)
    location = Column(String)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    phone = Column(String)
    dob = Column(DateTime)

    user = relationship("User", back_populates="profile")

    serialize_rules = ("-user.profile",)


class Role(db.Model):
    __tablename__ = "roles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Enum(RoleEnum))


class Application(db.Model):
    __tablename__ = "applications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    job_id = Column(UUID(as_uuid=True), ForeignKey("job.id"))
    created_at = Column(DateTime)
    status = Column(Enum(ApplicationStatusEnum))

    user = relationship("User", back_populates="applications")

    serialize_rules = ("-user.applications",)


class Education(db.Model):
    __tablename__ = "education"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    institution = Column(String)
    qualification = Column(String)
    course = Column(String)
    level = Column(Enum(EducationLevelEnum))
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))

class Experience(db.Model):
    __tablename__ = "experience"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    description = Column(Text)
    company = Column(String)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    job_title = Column(String)
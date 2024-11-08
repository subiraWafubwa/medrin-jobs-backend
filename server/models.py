from sqlalchemy import Column, String, Text, Integer, Float, DateTime, Enum, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy.ext.associationproxy import association_proxy
from datetime import datetime,timezone,timedelta

import uuid
import enum

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})
db = SQLAlchemy(metadata=metadata)


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
    hospitality="hospitality"
    real-estate="real-estate"
    cyber-security="cyber-security"

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
class Company(db.Model,SerializerMixin):
    __tablename__ = "company"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    phone_number=Column(String)
    location = Column(String)
    description = Column(String)
    mission = Column(String)
    vision = Column(String)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    user = relationship("User", back_populates="company")
    industries = relationship("IndustryCompany", back_populates="company")
    payments = relationship("Payment", back_populates="company")

    serialize_rules = ("-industries.company", "-payments.company",)

class Plan(db.Model,SerializerMixin):
    __tablename__ = "plans"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Enum(PlanEnum))
    price = Column(DECIMAL)

    payments = relationship("Payment", back_populates="plan")

    serialize_rules = ("-payments.plan",)

class Payment(db.Model,SerializerMixin):
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

class Job(db.Model,SerializerMixin):
    __tablename__ = "job"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String)
    description = Column(Text)
    created_at = Column(DateTime,default=lambda:datetime.now(timezone(timedelta(hours=3))))
    updated_at = Column(DateTime,default=lambda:datetime.now(timezone(timedelta(hours=3))))
    level = Column(Enum(JobLevelEnum))
    job_type = Column(Enum(JobTypeEnum))
    salary = Column(Float)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company.id"))

    responsibilities = relationship("JobResponsibility", back_populates="job")
    requirements = relationship("Requirement", back_populates="job")
    applications=relationship("Application",back_populates='job',cascade='all,delete-orphan')
    

    serialize_rules = ("-responsibilities.job", "-requirements.job","-applications.job")

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


class JobResponsibility(db.Model,SerializerMixin):
    __tablename__ = "job_responsibilities"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(Text)
    job_id = Column(UUID(as_uuid=True), ForeignKey("job.id"))

    job = relationship("Job", back_populates="responsibilities")

    serialize_rules = ("-job",)


class Requirement(db.Model,SerializerMixin):
    __tablename__ = "requirements"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(Text)
    job_id = Column(UUID(as_uuid=True), ForeignKey("job.id"))

    job = relationship("Job", back_populates="requirements")

    serialize_rules = ("-job",)


class User(db.Model,SerializerMixin):
    __tablename__ = "user"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True,nullable=False)
    password = Column(String,nullable=False)
    roles=Column(Enum(RoleEnum), nullable=False)
    code = Column(String)

    profile = relationship("Profile", uselist=False, back_populates="user",cascade='all,delete-orphan')
    applications = relationship("Application", back_populates="user",cascade='all,delete-orphan')
    company = relationship("Company", back_populates="user",cascade='all, delete-orphan')
    
    # user_roles=relationship('userRole',back_populates='user',cascade='all,delete-orphan')
    # roles=association_proxy('user_roles','Role',creator=lambda role_obj:UserRole(role=role_obj))
    
    

    # serialize_rules = ("-applications.user","-user_roles.user","-password")
    serialize_rules = ("-password","-user_roles","-company")
    
    
    def __repr__(self):
        return f"<User {self.profile} {self.email} {self.roles}>"
    
    #this method is going to be used when a user is creating an account or changing the password by the apis
    def set_password(self,password):
        self.password=generate_password_hash(password)
    
    #this method is going to be used when a user is logging into an account by the apis
    def check_password(self,password):
        return check_password_hash(password)
    
    #this method is going to be used when a user is logging into an account by the apis
    @classmethod
    def get_user_by_email(cls,email):
        return cls.query.filter_by(email=email).first()
    
    #this method is going to be used when a user is creating an account or when an admin is creating a new user by the apis
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        


class Profile(db.Model,SerializerMixin):
    __tablename__ = "profile"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String,nullable=False)
    last_name = Column(String,nullable=False)
    location = Column(String,nullable=False)
    phone = Column(String,nullable=False)
    dob = Column(DateTime)
    
    #Relationships
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    
    user = relationship("User", back_populates="profile")
    educations=relationship("Education",back_populates="profile")
    experiences=relationship('Experience',back_populates='profile')
    
    serialize_rules = ("-user","-educations.profile","-experiences.profile")

class Education(db.Model):
    __tablename__ = "education"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    institution = Column(String)
    qualification = Column(String)
    course = Column(String)
    level = Column(Enum(EducationLevelEnum))
    
    #Relationship
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profile.id"))
    profile=relationship("Profile",back_populates="educations")
    
    serialize_rules=('-profile',)

class Experience(db.Model):
    __tablename__ = "experience"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    description = Column(Text)
    company = Column(String)
    job_title = Column(String)
    
    #Relationships
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profile.id"))
    profile=relationship('Profile',back_populates='expereinces')
    
    serialize_rules=('-profile')

# class Role(db.Model):
#     __tablename__ = "roles"
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     name = Column(Enum(RoleEnum))

# class UserRole(db.Model,SerializerMixin):
#     __tablename__="user_roles"
#     id=Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
#     user_id=Column(UUID(as_uuid=True),ForeignKey('user.id'))
#     role_id=Column(UUID(as_uuid=True),ForeignKey('roles.id'))
    
#     role=relationship('Role',back_populates='user_roles')
#     user=relationship('User',back_populates='user_roles')
#     serialize_rules = ("-role.user_roles", "user.user_roles")

class Application(db.Model,SerializerMixin):
    __tablename__ = "applications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    job_id = Column(UUID(as_uuid=True), ForeignKey("job.id"))
    created_at = Column(DateTime,default=lambda:datetime.now(timezone(timedelta(hours=3))))
    status = Column(Enum(ApplicationStatusEnum))

    user = relationship("User", back_populates="applications")
    job=relationship("Job",back_populates='applications')
    shortlistings=relationship('Shortlisting',back_populates='application')

    serialize_rules = ("-user.applications","-shortlistings")

class Shortlisting(db.Model):
    __tablename__='shortlistings'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interview_date_time=Column(DateTime)
    application_id=db.Column(UUID(as_uuid=True),ForeignKey("applications.id"))
    application=relationship('Application',back_populates='shortlistings')
    
    
     
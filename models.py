from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

# SQLAlchemyインスタンスを作成（app.pyで初期化）
db = SQLAlchemy()


# Enumの定義
class EquipmentStatus(Enum):
    """遊具の状態"""
    NORMAL = "正常"
    CAUTION = "注意"
    DANGER = "危険"


class InspectionResult(Enum):
    """点検結果"""
    PASS = "合格"
    CONDITIONAL_PASS = "条件付き合格"
    FAIL = "不合格"


class OverallResult(Enum):
    """総合評価"""
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class UserRole(Enum):
    """ユーザーの役割"""
    ADMIN = "管理者"
    MANAGER = "責任者"
    INSPECTOR = "点検者"


class ReportStatus(Enum):
    """レポート状態"""
    DRAFT = "下書き"
    SUBMITTED = "提出済み"
    REVIEWED = "確認済み"
    APPROVED = "承認済み"


# 公園テーブル
class Parks(db.Model):
    __tablename__ = "parks"
    
    park_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    park_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey("users.employee_id"), nullable=True)
    
    # リレーション
    equipments = db.relationship("Equipments", back_populates="park", cascade="all, delete-orphan")
    reports = db.relationship("Reports", back_populates="park", cascade="all, delete-orphan")
    manager = db.relationship("Users", foreign_keys=[manager_id])
    
    def to_dict(self):
        return {
            "park_id": self.park_id,
            "park_name": self.park_name,
            "address": self.address,
            "manager_id": self.manager_id
        }


# 遊具テーブル
class Equipments(db.Model):
    __tablename__ = "equipments"
    
    equipment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    park_id = db.Column(db.Integer, db.ForeignKey("parks.park_id"), nullable=False)
    equipment_name = db.Column(db.String(100), nullable=False)
    install_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.Enum(EquipmentStatus), default=EquipmentStatus.NORMAL, nullable=False)
    
    # リレーション
    park = db.relationship("Parks", back_populates="equipments")
    inspections = db.relationship("Inspections", back_populates="equipment", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "equipment_id": self.equipment_id,
            "park_id": self.park_id,
            "equipment_name": self.equipment_name,
            "install_date": self.install_date.isoformat() if self.install_date else None,
            "status": self.status.value if self.status else None
        }


# 点検テーブル
class Inspections(db.Model):
    __tablename__ = "inspections"
    
    inspection_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipments.equipment_id"), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey("users.employee_id"), nullable=False)
    report_id = db.Column(db.Integer, db.ForeignKey("reports.report_id"), nullable=True)
    inspection_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    result = db.Column(db.Enum(InspectionResult), nullable=False)
    overall_result = db.Column(db.Enum(OverallResult), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    ai_result = db.Column(db.Text, nullable=True)  # AI分析結果
    image_url = db.Column(db.String(500), nullable=True)
    
    # リレーション
    equipment = db.relationship("Equipments", back_populates="inspections")
    employee = db.relationship("Users", back_populates="inspections")
    report = db.relationship("Reports", back_populates="inspections")
    
    def to_dict(self):
        return {
            "inspection_id": self.inspection_id,
            "equipment_id": self.equipment_id,
            "employee_id": self.employee_id,
            "report_id": self.report_id,
            "inspection_date": self.inspection_date.isoformat() if self.inspection_date else None,
            "result": self.result.value if self.result else None,
            "overall_result": self.overall_result.value if self.overall_result else None,
            "notes": self.notes,
            "ai_result": self.ai_result,
            "image_url": self.image_url
        }


# ユーザー/従業員テーブル
class Users(db.Model):
    __tablename__ = "users"
    
    employee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    mail = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(255), nullable=False)  # ハッシュ化して保存
    
    # リレーション
    inspections = db.relationship("Inspections", back_populates="employee")
    reports = db.relationship("Reports", back_populates="employee")
    
    def to_dict(self, include_password=False):
        data = {
            "employee_id": self.employee_id,
            "name": self.name,
            "role": self.role.value if self.role else None,
            "mail": self.mail,
            "phone": self.phone
        }
        if include_password:
            data["password"] = self.password
        return data


# レポートテーブル
class Reports(db.Model):
    __tablename__ = "reports"
    
    report_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    park_id = db.Column(db.Integer, db.ForeignKey("parks.park_id"), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey("users.employee_id"), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    file_url = db.Column(db.String(500), nullable=True)
    status = db.Column(db.Enum(ReportStatus), default=ReportStatus.DRAFT, nullable=False)
    
    # リレーション
    park = db.relationship("Parks", back_populates="reports")
    employee = db.relationship("Users", back_populates="reports")
    inspections = db.relationship("Inspections", back_populates="report")
    
    def to_dict(self):
        return {
            "report_id": self.report_id,
            "park_id": self.park_id,
            "employee_id": self.employee_id,
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "file_url": self.file_url,
            "status": self.status.value if self.status else None
        }
from flask_sqlalchemy import SQLAlchemyEnum, SQLAlchemy
from flask import Flask
from datetime import datetime
import enum
# SQLAlchemyインスタンスを作成
db = SQLAlchemy()

#Enumの定義
class RoleEnum(enum.Enum):
    """ユーザーの役割"""
    STAFF = "職員"
    INSPECTOR = "点検者"
    MANAGER = "管理者"

class EquipmentStatusEnum(enum.Enum):
    """遊具の状態"""
    NORMAL = "正常"
    CAUTION = "要注意"
    PROHIBITED = "使用禁止"

class InspectionResultEnum(enum.Enum):
    """点検結果"""
    NO_ISSUE = "異常なし"
    OBSERVATION = "経過観察"
    REPAIR_NEEDED = "要修理"

class OverallResultEnum(enum.Enum):
    """総合評価"""
    A = "A"
    B = "B"
    C = "C"
    D = "D"

class ReportStatusEnum(enum.Enum):
    """報告書の状態"""
    DRAFT = "下書き"
    SUBMITTED = "提出済"
    APPROVED = "承認済"
    REJECTED = "差戻"



#Userテーブル作成 
class User(db.Model):
    __tablename__= 'users'
    employee_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum(RoleEnum), nullable=False)
    mail = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password = db
    #リレーション
    managed_parks = db.relationship('Park', backref='manager', lazy=True)
    inspection_assignments = db.relationship('InspectionUser', backref='employee', lazy=True)
    created_reports = db.relationship('Report', backref='creator', lazy=True)
    
# 公園テーブル
class Park(db.Model):
    __tablename__ = 'parks'
    park_id = db.Column(db.Integer, primary_key=True)
    park_name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(500))
    manager_id = db.Column(db.Integer, db.ForeignKey('users.employee_id'))
    # リレーション
    equipments = db.relationship('Equipment', backref='park', lazy=True)
    reports = db.relationship('Report', backref='park', lazy=True)

# 遊具テーブル
class Equipment(db.Model):
    __tablename__ = 'equipments'
    equipment_id = db.Column(db.Integer, primary_key=True)
    park_id = db.Column(db.Integer, db.ForeignKey('parks.park_id'), nullable=False)
    equipment_name = db.Column(db.String(200), nullable=False)
    install_date = db.Column(db.Date)
    status = db.Column(db.Enum(EquipmentStatusEnum), default=EquipmentStatusEnum.NORMAL)
    # リレーション
    inspections = db.relationship('Inspection', backref='equipment', lazy=True)

# 点検記録テーブル
class Inspection(db.Model):
    __tablename__ = 'inspection'
    inspection_id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipments.equipment_id'), nullable=False)
    inspection_date = db.Column(db.DateTime, default=datetime.utcnow)
    result = db.Column(db.Enum(InspectionResultEnum))
    overall_result = db.Column(db.Enum(OverallResultEnum))
    notes = db.Column(db.Text)
    ai_result = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    
    # リレーション
    assigned_users = db.relationship('InspectionUser', backref='inspection', lazy=True)
    report_links = db.relationship('InspectionReport', backref='inspection', lazy=True)

# 報告書テーブル
class Report(db.Model):
    __tablename__ = 'reports'
    
    report_id = db.Column(db.Integer, primary_key=True)
    park_id = db.Column(db.Integer, db.ForeignKey('parks.park_id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.employee_id'), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    file_url = db.Column(db.String(500))
    status = db.Column(db.Enum(ReportStatusEnum), default=ReportStatusEnum.DRAFT)
    
    # リレーション
    inspection_links = db.relationship('InspectionReport', backref='report', lazy=True)


# 中間テーブル
class InspectionUser(db.Model):
    """点検担当者（中間テーブル）"""
    __tablename__ = 'inspection_users'
    
    inspection_user_id = db.Column(db.Integer, primary_key=True)
    inspection_id = db.Column(db.Integer, db.ForeignKey('inspection.inspection_id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.employee_id'), nullable=False)
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)

class InspectionReport(db.Model):
    """点検報告関連（中間テーブル）"""
    __tablename__ = 'inspection_reports'
    
    inspection_report_id = db.Column(db.Integer, primary_key=True)
    inspection_id = db.Column(db.Integer, db.ForeignKey('inspection.inspection_id'), nullable=False)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.report_id'), nullable=False)
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
    




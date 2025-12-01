from flask_sqlalchemy import SQLAlchemy
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
    password = db.Column(db.String(255), nullable=False)
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


# ============================================
# 【重要】点検記録テーブル（4部位対応版）
# ============================================
# 【設計方針】
# 現在：鎖（chain）のみ AI 推論
# 将来：継ぎ手、ポール、座面も推論できるように拡張可能な設計
# ============================================
class Inspection(db.Model):
    __tablename__ = 'inspection'
    inspection_id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipments.equipment_id'), nullable=False)
    inspection_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ========================================================
    # 【部位1】鎖（Chain）【現在：AI推論済み】
    # ========================================================
    # 検査結果（A/B/C）
    chain_result = db.Column(db.String(1))          # 'A', 'B', 'C'
    
    # AI推論の詳細情報
    chain_condition = db.Column(db.String(20))      # 'nomal' or 'rust'（推論結果）
    chain_confidence = db.Column(db.Float)          # 0.0~1.0（確信度）
    
    
    # ========================================================
    # 【部位2】継ぎ手（Joint）【現在：手動入力】
    # ========================================================
    # 継ぎ手：ポールとチェーンを接続する部分
    joint_result = db.Column(db.String(1))          # 'A', 'B', 'C'
    
    
    # ========================================================
    # 【部位3】ポール（Pole）【現在：手動入力】
    # ========================================================
    # ポール：遊具を支える縦の柱
    pole_result = db.Column(db.String(1))           # 'A', 'B', 'C'
    
    
    # ========================================================
    # 【部位4】座面（Seat）【現在：手動入力】
    # ========================================================
    # 座面：乗る部分
    seat_result = db.Column(db.String(1))           # 'A', 'B', 'C'
    
    
    # ========== 【旧カラム】互換性のため残す ==========
    result = db.Column(db.Enum(InspectionResultEnum))
    overall_result = db.Column(db.Enum(OverallResultEnum))
    chain_grade = db.Column(db.String(1))           # 'A', 'B', 'C'
    
    
    # ========== 【点検時の対応】 ==========
    actions_taken = db.Column(db.Text)              # 実施した措置
    notes = db.Column(db.Text)                      # 所見・備考
    ai_result = db.Column(db.Text)                  # AI推論の詳細（ログ用）
    
    
    # ========== 【点検後の対応計画】 ==========
    response_plan = db.Column(db.Text)              # 対応方針
    planned_response_date = db.Column(db.DateTime)  # 対応予定時期
    additional_remarks = db.Column(db.Text)         # その他備考
    
    
    # ========== 【写真関連】 ==========
    photo_path = db.Column(db.Text)                 # ファイルパス
    photo_data = db.Column(db.LargeBinary, nullable=True)  # 画像バイナリ
    photo_filename = db.Column(db.String(255), nullable=True)
    photo_uploaded_at = db.Column(db.DateTime, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    
    
    # ========== 【メタデータ】 ==========
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
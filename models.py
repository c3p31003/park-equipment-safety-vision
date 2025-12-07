<<<<<<< HEAD
from flask_sqlalchemy import SQLAlchemyEnum, SQLAlchemy
from flask import Flask
from datetime import datetime
import enum
# SQLAlchemyインスタンスを作成
db = SQLAlchemy()

#Enumの定義
class RoleEnum(enum.Enum):
    """ユーザーの役割"""
=======
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()

# ========================================
# Enum 定義
# ========================================
class RoleEnum(enum.Enum):
>>>>>>> origin/main
    STAFF = "職員"
    INSPECTOR = "点検者"
    MANAGER = "管理者"

class EquipmentStatusEnum(enum.Enum):
<<<<<<< HEAD
    """遊具の状態"""
=======
>>>>>>> origin/main
    NORMAL = "正常"
    CAUTION = "要注意"
    PROHIBITED = "使用禁止"

<<<<<<< HEAD
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
=======
class InspectionPartEnum(enum.Enum):
    """点検部位"""
    CHAIN = "chain"      # 鎖
    JOINT = "joint"      # 継ぎ手
    POLE = "pole"        # ポール
    SEAT = "seat"        # 座面

class ConditionEnum(enum.Enum):
    """部位の状態"""
    NORMAL = "normal"    # 正常
    RUST = "rust"        # 錆
    CRACK = "crack"      # ひび割れ
    WEAR = "wear"        # 摩耗
    LOOSE = "loose"      # 緩み
    DEFORM = "deform"    # 変形

class GradeEnum(enum.Enum):
    """判定等級"""
    A = "A"  # 異常なし
    B = "B"  # 経過観察
    C = "C"  # 要対応
    D = "D"  # 使用禁止

class ReportStatusEnum(enum.Enum):
>>>>>>> origin/main
    DRAFT = "下書き"
    SUBMITTED = "提出済"
    APPROVED = "承認済"
    REJECTED = "差戻"


<<<<<<< HEAD

#Userテーブル作成 
class User(db.Model):
    __tablename__= 'users'
=======
# ========================================
# User テーブル（変更なし）
# ========================================
class User(db.Model):
    __tablename__ = 'users'
>>>>>>> origin/main
    employee_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum(RoleEnum), nullable=False)
    mail = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
<<<<<<< HEAD
    password = db
    #リレーション
    managed_parks = db.relationship('Park', backref='manager', lazy=True)
    inspection_assignments = db.relationship('InspectionUser', backref='employee', lazy=True)
    created_reports = db.relationship('Report', backref='creator', lazy=True)
    
# 公園テーブル
=======
    password = db.Column(db.String(255), nullable=False)
    
    # リレーション
    managed_parks = db.relationship('Park', backref='manager', lazy=True)
    photographed_inspections = db.relationship('Inspection', 
                                               foreign_keys='Inspection.photographer_id',
                                               backref='photographer', lazy=True)
    inspected_inspections = db.relationship('Inspection',
                                           foreign_keys='Inspection.inspector_id',
                                           backref='inspector', lazy=True)
    created_reports = db.relationship('Report', backref='creator', lazy=True)


# ========================================
# Park テーブル（変更なし）
# ========================================
>>>>>>> origin/main
class Park(db.Model):
    __tablename__ = 'parks'
    park_id = db.Column(db.Integer, primary_key=True)
    park_name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(500))
    manager_id = db.Column(db.Integer, db.ForeignKey('users.employee_id'))
<<<<<<< HEAD
    # リレーション
    equipments = db.relationship('Equipment', backref='park', lazy=True)
    reports = db.relationship('Report', backref='park', lazy=True)

# 遊具テーブル
=======
    
    equipments = db.relationship('Equipment', backref='park', lazy=True)
    reports = db.relationship('Report', backref='park', lazy=True)


# ========================================
# Equipment テーブル（変更なし）
# ========================================
>>>>>>> origin/main
class Equipment(db.Model):
    __tablename__ = 'equipments'
    equipment_id = db.Column(db.Integer, primary_key=True)
    park_id = db.Column(db.Integer, db.ForeignKey('parks.park_id'), nullable=False)
    equipment_name = db.Column(db.String(200), nullable=False)
    install_date = db.Column(db.Date)
    status = db.Column(db.Enum(EquipmentStatusEnum), default=EquipmentStatusEnum.NORMAL)
<<<<<<< HEAD
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
    
=======
    
    inspections = db.relationship('Inspection', backref='equipment', lazy=True)


# ========================================
# 【改善版】Inspection テーブル
# ========================================
class Inspection(db.Model):
    """点検セッション（全体の記録）"""
    __tablename__ = 'inspection'
    
    # 基本情報
    inspection_id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipments.equipment_id'), nullable=False)
    
    # 日時情報
    inspection_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    photography_at = db.Column(db.DateTime)      # 撮影日時
    inspection_at = db.Column(db.DateTime)       # 検査完了日時
    
    # 担当者情報
    photographer_id = db.Column(db.Integer, db.ForeignKey('users.employee_id'))  # 撮影者
    inspector_id = db.Column(db.Integer, db.ForeignKey('users.employee_id'))     # 検査者
    
    # 全体の所見・対応
    overall_grade = db.Column(db.Enum(GradeEnum))     # 総合判定
    actions_taken = db.Column(db.Text)                # 実施した措置
    notes = db.Column(db.Text)                        # 所見
    response_plan = db.Column(db.Text)                # 対応方針
    planned_response_date = db.Column(db.DateTime)    # 対応予定日
    
    # メタデータ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーション
    details = db.relationship('InspectionDetail', backref='inspection', lazy=True, cascade='all, delete-orphan')
    photos = db.relationship('InspectionPhoto', backref='inspection', lazy=True, cascade='all, delete-orphan')
    report_links = db.relationship('InspectionReport', backref='inspection', lazy=True)


# ========================================
# 【新規】InspectionDetail テーブル
# ========================================
class InspectionDetail(db.Model):
    """部位ごとの検査詳細"""
    __tablename__ = 'inspection_detail'
    
    # 主キー
    detail_id = db.Column(db.Integer, primary_key=True)
    
    # 外部キー
    inspection_id = db.Column(db.Integer, db.ForeignKey('inspection.inspection_id'), nullable=False)
    
    # 部位情報
    part = db.Column(db.Enum(InspectionPartEnum), nullable=False)  # 'chain', 'joint', 'pole', 'seat'
    
    # 検査結果
    condition = db.Column(db.Enum(ConditionEnum))    # 'normal', 'rust', 'crack', ...
    grade = db.Column(db.Enum(GradeEnum))            # 'A', 'B', 'C', 'D'
    
    # AI判定情報
    is_ai_predicted = db.Column(db.Boolean, default=False)  # AI判定かどうか
    confidence = db.Column(db.Float)                         # 確信度 (0.0~1.0)
    ai_raw_result = db.Column(db.Text)                       # AI の生データ（JSON等）
    
    # 備考
    remarks = db.Column(db.Text)                    # この部位に関する備考
    
    # メタデータ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ユニーク制約：1つの点検で同じ部位は1回のみ
    __table_args__ = (
        db.UniqueConstraint('inspection_id', 'part', name='unique_inspection_part'),
    )


# ========================================
# 【新規】InspectionPhoto テーブル
# ========================================
class InspectionPhoto(db.Model):
    """点検写真管理"""
    __tablename__ = 'inspection_photo'
    
    # 主キー
    photo_id = db.Column(db.Integer, primary_key=True)
    
    # 外部キー
    inspection_id = db.Column(db.Integer, db.ForeignKey('inspection.inspection_id'), nullable=False)
    detail_id = db.Column(db.Integer, db.ForeignKey('inspection_detail.detail_id'))  # 部位と紐付け（任意）
    
    # 写真情報
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500))           # ローカルパス
    storage_url = db.Column(db.String(500))         # S3等のURL
    file_size = db.Column(db.Integer)               # バイト数
    mime_type = db.Column(db.String(50))            # 'image/png', 'image/jpeg'
    
    # バイナリデータ（オプション：小さい画像のみ）
    photo_data = db.Column(db.LargeBinary)
    
    # メタデータ
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.employee_id'))
    
    # リレーション
    uploader = db.relationship('User', backref='uploaded_photos')


# ========================================
# Report テーブル（変更なし）
# ========================================
class Report(db.Model):
    __tablename__ = 'reports'
>>>>>>> origin/main
    report_id = db.Column(db.Integer, primary_key=True)
    park_id = db.Column(db.Integer, db.ForeignKey('parks.park_id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.employee_id'), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    file_url = db.Column(db.String(500))
    status = db.Column(db.Enum(ReportStatusEnum), default=ReportStatusEnum.DRAFT)
    
<<<<<<< HEAD
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
    



=======
    inspection_links = db.relationship('InspectionReport', backref='report', lazy=True)


# ========================================
# 中間テーブル
# ========================================
class InspectionReport(db.Model):
    """点検-報告書 関連"""
    __tablename__ = 'inspection_reports'
    inspection_report_id = db.Column(db.Integer, primary_key=True)
    inspection_id = db.Column(db.Integer, db.ForeignKey('inspection.inspection_id'), nullable=False)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.report_id'), nullable=False)
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
>>>>>>> origin/main

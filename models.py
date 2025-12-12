from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum
from sqlalchemy.orm import validates

db = SQLAlchemy()


# Enum 定義
class RoleEnum(enum.Enum):
    STAFF = "事務職員"
    INSPECTOR = "点検者"
    MANAGER = "管理者"

class EquipmentStatusEnum(enum.Enum):
    A = "異常なし"
    B = "経過観察"
    C = "異常あり"

class InspectionPartEnum(enum.Enum):
    """点検部位"""
    CHAIN = "chain"      # 鎖
    JOINT = "joint"      # 継ぎ手
    POLE = "pole"        # ポール
    SEAT = "seat"        # 座面

class TypeOfAbnormalityEnum(enum.Enum):
    """部位の状態（日報、通常・詳細点検で使用）"""
    NORMAL = "normal"    # 正常
    RUST = "rust"        # 錆
    CRACK = "crack"      # ひび割れ

class GradeEnum(enum.Enum):
    """判定等級（指定管理者点検用）"""
    A = "健全" 
    B = "経過観察"  
    C = "要修繕・要対応"  
    D = "使用禁止措置" 

class ReportStatusEnum(enum.Enum):
    DRAFT = "下書き"
    SUBMITTED = "提出済"
    APPROVED = "承認済"
    REJECTED = "差戻"



# User テーブル（変更なし）
#引数にdb.Modelを入れることでDB テーブルと連動する Python オブジェクトになる
class User(db.Model):
    __tablename__ = 'users'
    employee_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum(RoleEnum), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
    # リレーション
    #Userが複数のParkを管理できる。backref='manager'でPark側からもアクセス可能にする。
    #lazy=Trueで必要になったときだけ読み込む。」
    assigned_parks = db.relationship('Park', foreign_keys='Park.inspector_id',backref='assigned_inspector', lazy=True)
    
    # STAFF が日報を作成（DailyReport 経由で Park に紐付く）
    created_daily_reports = db.relationship('DailyReport', backref='reporter', lazy=True)
    inspections = db.relationship('Inspection', foreign_keys='Inspection.inspector_id', backref='inspector', lazy=True)
    created_reports = db.relationship('Report', backref='creator', lazy=True)
    uploaded_inspection_photos = db.relationship('InspectionPhoto', backref='uploader', lazy=True)
    uploaded_daily_report_photos = db.relationship('DailyReportPhoto', backref='uploader', lazy=True)


# Park テーブル
class Park(db.Model):
    __tablename__ = 'parks'
    park_id = db.Column(db.Integer, primary_key=True)
    park_name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(500))
    inspector_id = db.Column(db.Integer, db.ForeignKey('users.employee_id'))

    # リレーション
    equipments = db.relationship('Equipment', backref='park', lazy=True)
    reports = db.relationship('Report', backref='park', lazy=True)
    daily_reports = db.relationship('DailyReport', backref='park', lazy=True)


    @staticmethod #デコレーター(クラスのインスタンス化なしで呼び出し可能)
    def validate_inspector(inspector_id):
        """STAFF または INSPECTOR role だけを許可"""
        if inspector_id is None:
            return True  # NULL はOK
        
        user = User.query.get(inspector_id)
        if not user:
            raise ValueError(f"ユーザーが見つかりません: {inspector_id}")
        
        allowed_roles = [RoleEnum.STAFF, RoleEnum.INSPECTOR]
        if user.role not in allowed_roles:
            raise ValueError(
                f"Park の inspector_id には STAFF または INSPECTOR のみ設定可能です。"
                f"入力: {user.role.value}"
            )
        return True

# Equipment テーブル（遊具情報）
class Equipments(db.Model):
    __tablename__ = 'equipments'
    equipment_id = db.Column(db.Integer, primary_key=True)
    park_id = db.Column(db.Integer, db.ForeignKey('parks.park_id'), nullable=False)
    equipment_name = db.Column(db.String(200), nullable=False, default="ブランコ")
    status = db.Column(db.Enum(EquipmentStatusEnum), default=EquipmentStatusEnum.A)

    # リレーション
    inspections = db.relationship('Inspection', backref='equipment', lazy=True)
    daily_report_details = db.relationship('DailyReportDetail', backref='equipment', lazy=True)

    def calculate_overall_grade(self):
        """
        直近の点検から総合評価を計算
        - 最新のInspectionを取得
        - InspectionDetailの全パーツ(chain, joint, pole, seat)をチェック
        - 1つでもCがあればC、その次がBならB、それ以外はA
        """
        if not self.inspections:
            return None
        
        # 最新の点検を取得
        latest_inspection = max(self.inspections, key=lambda x: x.inspection_date)
        
        if not latest_inspection.details:
            return None
        
        # 全部位の評価を取得
        grades = [detail.grade for detail in latest_inspection.details]
        
        # 判定ロジック：最も悪い評価を総合評価とする
        if GradeEnum.C in grades:
            return GradeEnum.C
        elif GradeEnum.B in grades:
            return GradeEnum.B
        else:
            return GradeEnum.A


# Inspection テーブル（指定管理者点検用）
class Inspection(db.Model):
    """点検セッション（全体の記録）- 専門家による通常点検"""
    __tablename__ = 'inspection'
    
    # 基本情報
    inspection_id = db.Column(db.Integer, primary_key=True, nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipments.equipment_id'), nullable=False)
    inspector_id = db.Column(db.Integer, db.ForeignKey('users.employee_id')) 
    # 日時情報
    inspection_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # 検査実施日時
    # 全体の評価
    overall_grade = db.Column(db.Enum(GradeEnum))     # 総合判定
    actions_taken = db.Column(db.Text)                # 実施した措置


    
    # メタデータ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーション
    details = db.relationship('InspectionDetail', backref='inspection', lazy=True, cascade='all, delete-orphan')
    photos = db.relationship('InspectionPhoto', backref='inspection', lazy=True, cascade='all, delete-orphan')
    report_links = db.relationship('InspectionReport', backref='inspection', lazy=True)
    
# バリデーション employee_id が点検者かどうかのチェック
    @validates('inspector_id')
    def validate_conducted_by_id(self, key, value):
        """inspection_id が点検者（INSPECTOR）ユーザーのみであることを確認"""
        if value is not None:
            user = User.query.get(value)
            if user is None:
                raise ValueError(f"Employee ID {value} は存在しません")
            if user.role != RoleEnum.INSPECTOR:
                raise ValueError(f"ユーザー {user.name} は点検者ではありません。点検者のみ設定可能です。")
        return value


# InspectionDetail テーブル
class InspectionDetail(db.Model):
    """部位ごとの検査詳細（専門家点検用）"""
    __tablename__ = 'inspection_detail'
    
    # 主キー
    detail_id = db.Column(db.Integer, primary_key=True)
    
    # 外部キー
    inspection_id = db.Column(db.Integer, db.ForeignKey('inspection.inspection_id'), nullable=False)
    
    # 部位情報
    part = db.Column(db.Enum(InspectionPartEnum), nullable=False)  # 'chain', 'joint', 'pole', 'seat'
    
    # 検査結果
    condition = db.Column(db.Enum(TypeOfAbnormalityEnum))    # 'normal', 'rust', 'crack'
    grade = db.Column(db.Enum(GradeEnum)) 
    
    # AI判定情報
    is_ai_predicted = db.Column(db.Boolean, default=False)  # AI判定かどうか
    confidence = db.Column(db.Float)                         # 確信度 (0.0~1.0)
    ai_json_detail_data = db.Column(db.Text)                       # AI の生データ（JSON等）
    
    # 備考
    remarks = db.Column(db.Text)                    # この部位に関する備考
    
    # メタデータ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ユニーク制約：1つの点検で同じ部位は1回のみ
    __table_args__ = (
        db.UniqueConstraint('inspection_id', 'part', name='unique_inspection_part'),
    )





# InspectionPhoto テーブル（専門家点検用写真）
class InspectionPhoto(db.Model):
    """専門家点検の写真管理"""
    __tablename__ = 'inspection_photos'
    
    # 主キー
    photo_id = db.Column(db.Integer, primary_key=True)
    
    # 外部キー
    inspection_id = db.Column(db.Integer, db.ForeignKey('inspection.inspection_id'), nullable=False)
    detail_id = db.Column(db.Integer, db.ForeignKey('inspection_detail.detail_id'), nullable=True)
    
    # 写真情報
    file_size = db.Column(db.Integer)
    photo_data = db.Column(db.LargeBinary)
    
    # メタデータ
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.employee_id'), nullable=False)
    
    # リレーション
    detail = db.relationship('InspectionDetail', foreign_keys=[detail_id], backref='inspection_photos')
    uploader = db.relationship('User', foreign_keys=[uploaded_by], backref='uploaded_inspection_photos')


# Report テーブル (通常点検の報告書)
class Report(db.Model):
    """報告書（専門家点検の年4回報告書）"""
    __tablename__ = 'reports'
    report_id = db.Column(db.Integer, primary_key=True)
    park_id = db.Column(db.Integer, db.ForeignKey('parks.park_id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.employee_id'), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    file_url = db.Column(db.String(500))
    status = db.Column(db.Enum(ReportStatusEnum), default=ReportStatusEnum.DRAFT)
    
    inspection_links = db.relationship('InspectionReport', backref='report', lazy=True)

# 中間テーブル
class InspectionReport(db.Model):
    """点検-報告書 関連（専門家点検用）"""
    __tablename__ = 'inspection_reports'
    inspection_report_id = db.Column(db.Integer, primary_key=True)
    inspection_id = db.Column(db.Integer, db.ForeignKey('inspection.inspection_id'), nullable=False)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.report_id'), nullable=False)
    added_date = db.Column(db.DateTime, default=datetime.utcnow)



#DailyReport テーブル
class DailyReport(db.Model):
    """日報（毎日、事務所スタッフによる簡易異常報告）"""
    __tablename__ = 'daily_reports'
    
    # 主キー
    daily_report_id = db.Column(db.Integer, primary_key=True)
    
    # 外部キー
    park_id = db.Column(db.Integer, db.ForeignKey('parks.park_id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.employee_id'), nullable=False)
    
    # 報告情報
    report_date = db.Column(db.DateTime, nullable=False)  # 報告日時
    notes = db.Column(db.Text)                            # 備考
    
    # メタデータ
    # created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーション
    details = db.relationship('DailyReportDetail', backref='daily_report', lazy=True, cascade='all, delete-orphan')
    photos = db.relationship('DailyReportPhoto', backref='daily_report', lazy=True, cascade='all, delete-orphan')



# DailyReportDetail テーブル
class DailyReportDetail(db.Model):
    """日報の異常記録（遊具ごとの異常を記録）"""
    __tablename__ = 'daily_report_detail'
    
    # 主キー
    detail_id = db.Column(db.Integer, primary_key=True)
    
    # 外部キー
    daily_report_id = db.Column(db.Integer, db.ForeignKey('daily_reports.daily_report_id'), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipments.equipment_id'), nullable=False)
    part = db.Column(db.Enum(InspectionPartEnum), nullable=False)
    # 異常情報
    condition = db.Column(db.Enum(TypeOfAbnormalityEnum), nullable=False) 
    deterioration_degree = db.Column(db.Float)                                # 劣化度（0.0～1.0、AI自動計算）
    remarks = db.Column(db.Text)                                    # この異常に関する備考
    
    # メタデータ
    # created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    





# DailyReportPhoto テーブル（日報用写真）
class DailyReportPhoto(db.Model):
    """日報の写真管理"""
    __tablename__ = 'daily_report_photos'
    
    # 主キー
    photo_id = db.Column(db.Integer, primary_key=True)
    
    # 外部キー
    daily_report_id = db.Column(db.Integer, db.ForeignKey('daily_reports.daily_report_id'), nullable=False)
    daily_detail_id = db.Column(db.Integer, db.ForeignKey('daily_report_detail.detail_id'), nullable=True)
    
    # 写真情報
    file_size = db.Column(db.Integer)
    photo_data = db.Column(db.LargeBinary)
    
    # メタデータ
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.employee_id'), nullable=False)
    
    # リレーション
    daily_detail = db.relationship('DailyReportDetail', foreign_keys=[daily_detail_id], backref='daily_report_photos')
    uploader = db.relationship('User', foreign_keys=[uploaded_by], backref='uploaded_daily_report_photos')











"""
テーブル作成スクリプト - 公園遊具安全点検業務軽減システム

使用方法:
  python create_tables.py

注意:
  - 開発環境での初期セットアップ用
  - 本番環境では Flask-Migrate を使用してください
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from models import db, Parks, Equipments, Inspections, Users, Reports
from models import EquipmentStatus, InspectionResult, OverallResult, UserRole, ReportStatus
from datetime import datetime, date

# .env 読み込み
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


def create_app():
    """Flaskアプリケーション作成"""
    app = Flask(__name__)
    
    # DB接続設定
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:3306/{os.getenv('DB_NAME')}?charset=utf8mb4"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # SQLAlchemy 初期化
    db.init_app(app)
    
    return app


def create_tables():
    """テーブル作成"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("公園遊具安全点検システム - テーブル作成")
        print("=" * 60)
        
        # 全テーブルを作成
        db.create_all()
        print("✓ テーブルの作成が完了しました\n")
        
        # 作成されたテーブルの一覧を表示
        print("作成されたテーブル:")
        for table in db.metadata.tables.keys():
            print(f"  ✓ {table}")
        print()


def reset_tables():
    """テーブルをリセット（全データ削除）"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("⚠️  警告: 全データを削除してテーブルを再作成します")
        print("=" * 60)
        response = input("続行しますか? (yes/no): ")
        
        if response.lower() != "yes":
            print("キャンセルしました")
            return
        
        print("\n全テーブルを削除中...")
        db.drop_all()
        print("✓ テーブルを削除しました")
        
        print("\nテーブルを再作成中...")
        db.create_all()
        print("✓ テーブルの再作成が完了しました\n")


def insert_sample_data():
    """サンプルデータを挿入"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("サンプルデータを挿入中...")
        print("=" * 60)
        
        try:
            # ユーザーを作成
            admin = Users(
                name="管理者太郎",
                role=UserRole.ADMIN,
                mail="admin@example.com",
                phone="090-1234-5678",
                password="hashed_password_123"  # 実際はハッシュ化が必要
            )
            
            inspector1 = Users(
                name="点検花子",
                role=UserRole.INSPECTOR,
                mail="inspector1@example.com",
                phone="090-2345-6789",
                password="hashed_password_456"
            )
            
            manager1 = Users(
                name="責任者次郎",
                role=UserRole.MANAGER,
                mail="manager1@example.com",
                phone="090-3456-7890",
                password="hashed_password_789"
            )
            
            db.session.add_all([admin, inspector1, manager1])
            db.session.commit()
            print("✓ ユーザーを作成しました")
            
            # 公園を作成
            park1 = Parks(
                park_name="中央公園",
                address="東京都千代田区1-1-1",
                manager_id=manager1.employee_id
            )
            
            park2 = Parks(
                park_name="西公園",
                address="東京都新宿区2-2-2",
                manager_id=manager1.employee_id
            )
            
            db.session.add_all([park1, park2])
            db.session.commit()
            print("✓ 公園を作成しました")
            
            # 遊具を作成
            equipment1 = Equipments(
                park_id=park1.park_id,
                equipment_name="ブランコ",
                install_date=date(2020, 4, 1),
                status=EquipmentStatus.NORMAL
            )
            
            equipment2 = Equipments(
                park_id=park1.park_id,
                equipment_name="滑り台",
                install_date=date(2019, 5, 15),
                status=EquipmentStatus.CAUTION
            )
            
            equipment3 = Equipments(
                park_id=park2.park_id,
                equipment_name="ジャングルジム",
                install_date=date(2021, 3, 10),
                status=EquipmentStatus.NORMAL
            )
            
            db.session.add_all([equipment1, equipment2, equipment3])
            db.session.commit()
            print("✓ 遊具を作成しました")
            
            # レポートを作成
            report1 = Reports(
                park_id=park1.park_id,
                employee_id=inspector1.employee_id,
                file_url="/reports/2024-01-report.pdf",
                status=ReportStatus.SUBMITTED
            )
            
            db.session.add(report1)
            db.session.commit()
            print("✓ レポートを作成しました")
            
            # 点検記録を作成
            inspection1 = Inspections(
                equipment_id=equipment1.equipment_id,
                employee_id=inspector1.employee_id,
                report_id=report1.report_id,
                result=InspectionResult.PASS,
                overall_result=OverallResult.A,
                notes="特に問題なし",
                ai_result="AI分析: 異常は検出されませんでした",
                image_url="/images/inspection_001.jpg"
            )
            
            inspection2 = Inspections(
                equipment_id=equipment2.equipment_id,
                employee_id=inspector1.employee_id,
                report_id=report1.report_id,
                result=InspectionResult.CONDITIONAL_PASS,
                overall_result=OverallResult.B,
                notes="軽微な錆が確認された",
                ai_result="AI分析: 表面に錆の兆候があります",
                image_url="/images/inspection_002.jpg"
            )
            
            db.session.add_all([inspection1, inspection2])
            db.session.commit()
            print("✓ 点検記録を作成しました")
            
            print("\n" + "=" * 60)
            print("✓ サンプルデータの挿入が完了しました")
            print("=" * 60)
            print("\n挿入されたデータ:")
            print(f"  - ユーザー: {Users.query.count()}件")
            print(f"  - 公園: {Parks.query.count()}件")
            print(f"  - 遊具: {Equipments.query.count()}件")
            print(f"  - レポート: {Reports.query.count()}件")
            print(f"  - 点検記録: {Inspections.query.count()}件")
            print()
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ エラーが発生しました: {str(e)}")


def show_menu():
    """メニュー表示"""
    print("\n" + "=" * 60)
    print("公園遊具安全点検システム - データベース管理")
    print("=" * 60)
    print("1. テーブルを作成")
    print("2. テーブルをリセット（全データ削除）")
    print("3. サンプルデータを挿入")
    print("4. 終了")
    print("=" * 60)
    return input("選択してください (1-4): ")


if __name__ == "__main__":
    while True:
        choice = show_menu()
        
        if choice == "1":
            create_tables()
        elif choice == "2":
            reset_tables()
        elif choice == "3":
            insert_sample_data()
        elif choice == "4":
            print("\n終了します")
            break
        else:
            print("\n無効な選択です。1-4を入力してください。")
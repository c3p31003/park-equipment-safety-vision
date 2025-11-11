import React, { useState, useRef, useEffect } from 'react';
import back from './assets/back.svg';
import './TakePhotoPage.css';  // スタイル（別途作成）

export default function TakePhotoPage() {
  // ====== 状態管理 ======
  const [isCameraOn, setIsCameraOn] = useState(false);        // カメラ起動中か
  const [capturedImage, setCapturedImage] = useState(null);   // キャプチャ後の画像（Base64）
  const [isLoading, setIsLoading] = useState(false);          // 送信中か
  const [message, setMessage] = useState(null);               // メッセージ（成功/エラー）
  const [equipmentId, setEquipmentId] = useState(1);          // 遊具ID（必要に応じて変更）

  // ====== DOM参照 ======
  const videoRef = useRef();      // ビデオ要素への参照
  const canvasRef = useRef();     // Canvas要素への参照
  let stream = null;              // ストリーム管理用（クリーンアップで使用）

  // ====== 1. カメラ起動処理 ======
    const startCamera = async () => {
        try {
        setIsCameraOn(true);
        setMessage(null);

        // 制約条件：スマホなら背面カメラ、PCなら前面カメラ
        const constraints = {
            video: {
            facingMode: {
                ideal: 'environment'  // 背面カメラを優先（失敗時は前面に自動切替）
            }
            }
        };

        // ブラウザのカメラストリームを取得
        stream = await navigator.mediaDevices.getUserMedia(constraints);

        // Videoタグに割り当て
        if (videoRef.current) {
            videoRef.current.srcObject = stream;
            videoRef.current.play();
        }
        } catch (error) {
        console.error('カメラの起動に失敗しました:', error);
        setMessage('カメラの起動に失敗しました');
        setIsCameraOn(false);
        }
    };

    // ====== 2. カメラ停止処理 ======
    const stopCamera = () => {
        if (stream) {
        // ストリームのすべてのトラック（ビデオ・オーディオ）を停止
        stream.getTracks().forEach(track => track.stop());
        stream = null;
        }
        if (videoRef.current) {
        videoRef.current.srcObject = null;
        }
        setIsCameraOn(false);
    };

    // ====== 3. 写真撮影処理 ======
    const capturePhoto = () => {
        if (!videoRef.current || !canvasRef.current) return;

        const canvas = canvasRef.current;
        const video = videoRef.current;
        const ctx = canvas.getContext('2d');

        // Canvas のサイズをビデオサイズに合わせる
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // ビデオの現在フレームをCanvasに描画
        ctx.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);

        // Canvas を Base64文字列に変換
        // toDataURL('image/png') は "data:image/png;base64,..." の形式
        const imageBase64 = canvas.toDataURL('image/png');
        setCapturedImage(imageBase64);
        console.log('写真をキャプチャしました');
    };

    // ====== 4. 写真送信処理（Backend に POST） ======
    const submitPhoto = async () => {
        if (!capturedImage) {
        setMessage('写真を撮影してください');
        return;
        }

        setIsLoading(true);
        setMessage(null);

        try {
        // 【重要】ここで API エンドポイントを指定
        // EC2の IP またはドメインに合わせてください
        const serverUrl = 'http://your-ec2-ip:5000/api/upload_photo';
        // または HTTPS なら: 'https://your-domain.com/api/upload_photo'

        const response = await fetch(serverUrl, {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
            },
            body: JSON.stringify({
            photo_data: capturedImage,           // Base64 文字列
            equipment_id: equipmentId,           // 遊具ID
            filename: `inspection_${new Date().toISOString().slice(0, 10)}.png`
            })
        });

        if (!response.ok) {
            throw new Error(`Server responded with ${response.status}`);
        }

        const result = await response.json();
        setMessage(`✓ 送信成功！ (ID: ${result.photo_id})`);
        
        // 成功後、キャプチャをリセット
        setTimeout(() => {
            setCapturedImage(null);
            setMessage(null);
        }, 2000);

        } catch (error) {
        console.error('写真送信エラー:', error);
        setMessage(`✗ 送信失敗: ${error.message}`);
        } finally {
        setIsLoading(false);
        }
    };

    // ====== 5. 再撮影処理 ======
    const retakePhoto = () => {
        setCapturedImage(null);
        setMessage(null);
        // カメラはまだ起動している状態で再撮影可能
    };

  // ====== 6. クリーンアップ（コンポーネント卸載時） ======
    useEffect(() => {
    return () => {
        stopCamera();  // コンポーネント破棄時にカメラを停止
        };
    }, []);

    // ====== 戻るボタン処理 ======
    const handleBack = () => {
        stopCamera();
        setCapturedImage(null);
        // 必要に応じてルーティング: navigate('/previous-page')
    };

    // ========================================
    // レンダリング
    // ========================================
    
    return (
        <div className="take-photo-container">
        <header className="header">
            <h1>遊具管理システム</h1>
        </header>

        <div className="content">
            <button className="back-button" onClick={handleBack}>
            <img src={back} alt="戻る" />
            <p>戻る</p>
            </button>

            {/* ===== 状態1: カメラ未起動 ===== */}
            {!isCameraOn && !capturedImage && (
            <div className="camera-start-section">
                <button className="camera-start-btn" onClick={startCamera}>
                📷 カメラを起動
                </button>
            </div>
            )}

            {/* ===== 状態2: カメラ起動中 ===== */}
            {isCameraOn && !capturedImage && (
            <div className="camera-section">
                <video
                ref={videoRef}
                className="camera-stream"
                playsInline
                />
                <button className="capture-btn" onClick={capturePhoto}>
                📷 撮 影
                </button>
                <button className="close-camera-btn" onClick={stopCamera}>
                ✕ 閉じる
                </button>
            </div>
            )}

            {/* ===== 状態3: 写真キャプチャ完了（プレビュー表示） ===== */}
            {capturedImage && (
            <div className="preview-section">
                <img src={capturedImage} alt="撮影した写真" className="preview-image" />
                <div className="button-group">
                <button
                    className="retake-btn"
                    onClick={retakePhoto}
                    disabled={isLoading}
                >
                    🔄 再撮影
                </button>
                <button
                    className="submit-btn"
                    onClick={submitPhoto}
                    disabled={isLoading}
                >
                    {isLoading ? '送信中...' : '✓ 送信'}
                </button>
                </div>
            </div>
            )}

            {/* ===== メッセージ表示 ===== */}
            {message && (
            <div className={`message ${message.includes('✗') ? 'error' : 'success'}`}>
                {message}
            </div>
            )}
        </div>

        {/* キャプチャ用Canvas（非表示） */}
        <canvas ref={canvasRef} style={{ display: 'none' }} />
        </div>
    );
}
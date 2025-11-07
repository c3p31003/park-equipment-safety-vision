import React, { useState, useRef, useEffect } from 'react';
import edit from './assets/edit.svg';
import add from './assets/add.svg';
import remove from './assets/remove.svg';
import save from './assets/save.svg';
import back from './assets/back.svg';
import { useNavigate } from 'react-router-dom';
import { BrowserMultiFormatReader } from '@zxing/browser';
import { NotFoundException } from '@zxing/library';


export default function RegisterPage() {
    // const [data, setData] = useState({ name: '鯖みそ煮', expDate: '2027年4月1日', count: 2, note: '半額引' });
    // const [editName, setEditName] = useState(false);
    // const [editDate, setEditDate] = useState(false);
    // const [editMemo, setEditMemo] = useState(false);
    const [isCameraOn, setIsCameraOn] = useState(false);
    // const [barcodeData, setBarcodeData] = useState(null);
    const [error, setError] = useState(null);

    const videoRef = useRef();
    const canvasRef = useRef();
    const barcodeReader = new BrowserMultiFormatReader();

    const startCamera = async () => {
    setIsCameraOn(true);
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
        video: true
        });
        if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
        setBarcodeData(null);
        setError(null);
        }
    } catch (error) {
        console.log(error);
    }
    };

    const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop());
        videoRef.current.srcObject = null;
        setIsCameraOn(false);
        setBarcodeData(9784478116982)
    }
    };

    const handleCapture = () => {
    if (videoRef.current && canvasRef.current) {
        const canvas = canvasRef.current;
        const video = videoRef.current;

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0, video.videoWidth, video.videoHeight);

        try {
        const result = barcodeReader.decodeFromCanvas(canvas);
        setBarcodeData(result.getText());
        stopCamera();
        } catch (error) {
        if (error instanceof NotFoundException) {
            console.log('No barcode found in the image');
        } else {
            console.log(error);
        }
        }
    }
    };

    useEffect(() => {
    return () => {
        stopCamera();
    };
    }, []);

    const navigate = useNavigate();

    const handleAdd = () => {
    setData(prev => {
        return {
        ...prev,
        count: prev.count + 1
        };
    });
    };

    const handleRemove = () => {
    if (data.count < 1) return;
    setData(prev => {
        return {
        ...prev,
        count: prev.count - 1
        };
    });
    };
    const handleChange = e => {
    setData(prev => {
        return {
        ...prev,
        [e.target.name]: e.target.value
        };
    });
    };
    const submit = async () => {
    // implement POST to flask
    try {
        if (!barcodeData) {
        throw new Error('There was no barcode data');
        } else {
        const response = await fetch("http://54.64.250.189:5000/api/fetch_and_add_item", {
            method: 'POST',
            headers: {
            "Content-Type": 'application/json'
            },
            body: JSON.stringify({ item_code: barcodeData })
        });

        if (!response.ok) {
            throw new Error('There was a problem sending data to the server');
        } else {
            console.log('Sucessfully sent the code');
        }
        }
        console.log(data);
        navigate('/overview');
    } catch (error) {
        console.log(error);
    }
    };
    return (
    <div>
        <h1 className='text-gray' style={{ marginBottom: 0 }}>手動入力</h1>
        <h2 className='text-gray' style={{ fontWeight: 'normal', marginTop: 0 }}>商品登録</h2>
        {!isCameraOn &&
        <>
            <div onClick={startCamera} style={{ backgroundColor: "#e7e7e7", borderRadius: '2em', display: 'flex', justifyContent: 'center', padding: '1em 0' }}>
            <svg xmlns="http://www.w3.org/2000/svg" width="134" height="134" viewBox="0 0 134 134" fill="none">
                <path d="M108.593 29.6712H94.1888L87.106 19.0496C86.7265 18.4809 86.2127 18.0145 85.6099 17.6918C85.0071 17.3692 84.3341 17.2001 83.6504 17.1997H50.393C49.7093 17.2001 49.0363 17.3692 48.4335 17.6918C47.8307 18.0145 47.3168 18.4809 46.9374 19.0496L39.8494 29.6712H25.45C22.1424 29.6712 18.9702 30.9852 16.6313 33.324C14.2925 35.6629 12.9785 38.8351 12.9785 42.1427V100.343C12.9785 103.651 14.2925 106.823 16.6313 109.162C18.9702 111.501 22.1424 112.815 25.45 112.815H108.593C111.901 112.815 115.073 111.501 117.412 109.162C119.751 106.823 121.065 103.651 121.065 100.343V42.1427C121.065 38.8351 119.751 35.6629 117.412 33.324C115.073 30.9852 111.901 29.6712 108.593 29.6712ZM112.751 100.343C112.751 101.446 112.313 102.503 111.533 103.283C110.753 104.062 109.696 104.5 108.593 104.5H25.45C24.3475 104.5 23.2901 104.062 22.5105 103.283C21.7308 102.503 21.2929 101.446 21.2929 100.343V42.1427C21.2929 41.0402 21.7308 39.9828 22.5105 39.2032C23.2901 38.4235 24.3475 37.9855 25.45 37.9855H42.0787C42.7633 37.986 43.4374 37.8174 44.0411 37.4946C44.6449 37.1719 45.1596 36.7051 45.5395 36.1356L52.6171 25.514H81.4211L88.5039 36.1356C88.8838 36.7051 89.3985 37.1719 90.0023 37.4946C90.606 37.8174 91.2801 37.986 91.9647 37.9855H108.593C109.696 37.9855 110.753 38.4235 111.533 39.2032C112.313 39.9828 112.751 41.0402 112.751 42.1427V100.343ZM67.0217 46.2999C62.4995 46.2999 58.0789 47.6409 54.3189 50.1532C50.5589 52.6656 47.6283 56.2365 45.8977 60.4145C44.1672 64.5924 43.7144 69.1897 44.5966 73.6249C45.4788 78.0602 47.6565 82.1342 50.8541 85.3319C54.0518 88.5295 58.1258 90.7072 62.5611 91.5894C66.9963 92.4716 71.5936 92.0188 75.7715 90.2883C79.9495 88.5577 83.5204 85.6271 86.0328 81.8671C88.5451 78.1071 89.8861 73.6865 89.8861 69.1643C89.8792 63.1024 87.4681 57.2907 83.1817 53.0043C78.8953 48.7179 73.0836 46.3068 67.0217 46.2999ZM67.0217 83.7144C64.144 83.7144 61.3308 82.861 58.9381 81.2623C56.5453 79.6635 54.6804 77.3911 53.5792 74.7324C52.4779 72.0737 52.1898 69.1482 52.7512 66.3257C53.3126 63.5033 54.6984 60.9107 56.7332 58.8758C58.7681 56.841 61.3607 55.4552 64.1831 54.8938C67.0056 54.3324 69.9311 54.6205 72.5898 55.7218C75.2484 56.823 77.5209 58.688 79.1196 61.0807C80.7184 63.4735 81.5718 66.2866 81.5718 69.1643C81.5718 73.0232 80.0388 76.7241 77.3102 79.4528C74.5815 82.1814 70.8806 83.7144 67.0217 83.7144Z" fill="#C1C1C1" />
            </svg>
            </div>
            <div style={{ borderRadius: '1em', backgroundColor: '#f2f2f2', padding: '.5em 1.5em', marginTop: '2em', display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', alignItems: 'center' }} className='text-gray'>
            <h3 style={{ fontWeight: '500' }}>商品名:</h3>
            {!editName && <h3 style={{ fontWeight: '400' }}>{data.name}</h3>}
            {editName && <input type="text" value={data.name} onChange={handleChange} name='name' style={{ borderRadius: '100px', border: 'none', padding: '.5em' }} />}
            <img src={editName ? save : edit} alt="edit and save logo" style={{ justifySelf: 'end' }} onClick={() => setEditName(prev => !prev)} />
            <h3 style={{ fontWeight: '500' }}>消費期限:</h3>
            {!editDate && <h3 style={{ fontWeight: '400' }}>{data.expDate}</h3>}
            {editDate && <input type="date" name="expDate" id="expDate" value={data.expDate} onChange={handleChange} />}
            <img src={editDate ? save : edit} alt="edit and save logo" style={{ justifySelf: 'end' }} onClick={() => setEditDate(prev => !prev)} />
            <h3 style={{ fontWeight: '500' }}>個数:</h3>
            {/* <h3 style={{ fontWeight: '400' }}>2027年4月1日</h3> */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '.5em' }}>
                <h3>x{data.count}</h3>
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                <img height={'20em'} src={add} alt="green plus icon" onClick={handleAdd} />
                <img height={'20em'} src={remove} alt="red remove icon" onClick={handleRemove} />
                </div>
            </div>
            <h3 style={{ fontWeight: '500', gridColumnStart: 1 }}>メモ:</h3>
            {!editMemo && <h3 style={{ fontWeight: '400' }}>{data.note}</h3>}
            {editMemo && <input type="text" value={data.note} name='note' onChange={handleChange} style={{ borderRadius: '100px', border: 'none', padding: '.5em' }} />}
            <img src={editMemo ? save : edit} alt="edit and save logo" style={{ justifySelf: 'end' }} onClick={() => setEditMemo(prev => !prev)} />
            </div>
            <div style={{ paddingTop: '1em' }}>
            <button type="button" onClick={submit} style={{ backgroundColor: '#50B4AA', border: 'none', color: 'white', fontSize: '2em', fontFamily: 'Zen Maru Gothic', borderRadius: '.25em' }}>確認</button>
            </div>
        </>}
        {isCameraOn && (
        <div>
            <video ref={videoRef} style={{ width: '100%', maxWidth: '500px', border: 'none', borderRadius: '1em' }} />
            <canvas ref={canvasRef} style={{ display: 'none' }} />
            <div style={{ display: 'flex', justifyContent: 'center', position: 'relative' }}>
            <img src={back} style={{ position: 'absolute', left: 0 }} onClick={stopCamera} />
            <div onClick={stopCamera} style={{ backgroundColor: 'white', height: '2em', width: '2em', border: '.5em solid #50B4AA', borderRadius: '100px' }}></div>
            </div>
        </div>
        )}
        {barcodeData && (
        <p>{barcodeData}</p>
        )}
    </div>
    );
}
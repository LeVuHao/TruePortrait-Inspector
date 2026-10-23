import React, { useState, useRef, useCallback } from 'react';
import './App.css';
import { 
  Upload, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Layers, 
  Camera, 
  Maximize2, 
  User, 
  Sun, 
  Zap, 
  Square, 
  BarChart2, 
  RotateCcw,
  Sparkles,
  Lightbulb,
  Download,
  Video,
  VideoOff,
  Aperture,
  X
} from 'lucide-react';



export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState('original');
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  // === WEBCAM STATE ===
  const [showCamera, setShowCamera] = useState(false);
  const [cameraStream, setCameraStream] = useState(null);
  const [cameraReady, setCameraReady] = useState(false);
  const [countdown, setCountdown] = useState(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const handleFileSelect = (file) => {
    if (!file) return;
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
    analyzeImage(file);
  };

  // === WEBCAM FUNCTIONS ===
  const openCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 960 }, facingMode: 'user' },
        audio: false
      });
      setCameraStream(stream);
      setShowCamera(true);
      setCameraReady(false);
      setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.onloadedmetadata = () => setCameraReady(true);
        }
      }, 100);
    } catch (err) {
      alert('Không thể mở webcam. Hãy cho phép trình duyệt truy cập camera trong cài đặt.');
    }
  }, []);

  const closeCamera = useCallback(() => {
    if (cameraStream) {
      cameraStream.getTracks().forEach(t => t.stop());
      setCameraStream(null);
    }
    setShowCamera(false);
    setCameraReady(false);
    setCountdown(null);
  }, [cameraStream]);

  const capturePhoto = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return;
    let count = 3;
    setCountdown(count);
    const tick = setInterval(() => {
      count -= 1;
      if (count > 0) {
        setCountdown(count);
      } else {
        clearInterval(tick);
        setCountdown('📸');
        setTimeout(() => {
          const video = videoRef.current;
          const canvas = canvasRef.current;
          if (!video || !canvas) return;
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          const ctx = canvas.getContext('2d');
          // Flip horizontally (mirror)
          ctx.translate(canvas.width, 0);
          ctx.scale(-1, 1);
          ctx.drawImage(video, 0, 0);
          canvas.toBlob((blob) => {
            const file = new File([blob], 'webcam_photo.jpg', { type: 'image/jpeg' });
            closeCamera();
            handleFileSelect(file);
          }, 'image/jpeg', 0.95);
        }, 300);
      }
    }, 1000);
  }, [closeCamera]);


  const analyzeImage = async (file) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('preset', 'STANDARD_ID_PHOTO');

    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Lỗi khi gửi yêu cầu phân tích');
      }

      const data = await response.json();
      setResult(data);
      setActiveTab('face_bbox'); // Mặc định chuyển sang xem phát hiện khuôn mặt khi có kết quả
    } catch (err) {
      alert(`Lỗi: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const loadSample = async (sampleType) => {
    try {
      setLoading(true);
      // Giả lập load mẫu
      const filename = sampleType === 'standard' ? 'sample_standard.jpg' : 'sample_blurry.jpg';
      const res = await fetch(`http://127.0.0.1:8000/`);
      alert("Đã kết nối Backend API sẵn sàng! Hãy kéo thả ảnh thẻ của bạn vào để kiểm tra.");
    } catch (e) {
      alert("Backend API đang khởi động, vui lòng thử lại sau vài giây.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadStandardized = () => {
    if (!result?.visual_assets?.standardized) return;
    const link = document.createElement('a');
    link.href = result.visual_assets.standardized;
    link.download = 'PhotoCheck_Anh_De_Xuat_3x4.jpg';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };


  const getActiveImageSrc = () => {
    if (!result || !result.visual_assets) return previewUrl;
    switch (activeTab) {
      case 'original':
        return result.visual_assets.original || previewUrl;
      case 'face_bbox':
        return result.visual_assets.face_bbox || previewUrl;
      case 'clahe_enhanced':
        return result.visual_assets.clahe_enhanced || previewUrl;
      case 'grayscale':
        return result.visual_assets.grayscale || previewUrl;
      default:
        return previewUrl;
    }
  };


  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="header-brand">
          <div className="brand-icon">
            <Sparkles size={22} />
          </div>
          <div>
            <h1 className="brand-title">PhotoCheck Pro</h1>
            <p className="brand-subtitle">Chuyên đề: Trích xuất Đặc trưng Toàn cục (Global Features & IQA)</p>
          </div>
        </div>
        <div className="header-controls">
          <div className="preset-badge">
            <Square size={14} />
            <span>Preset: STANDARD_ID_PHOTO (3:4 & 4:6, Min 400x500)</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        <div className="grid-workspace">
          
          {/* CỘT TRÁI: VISUAL CANVAS & STEP-BY-STEP */}
          <div className="card-glass">
            {!previewUrl ? (
              <div 
                className={`upload-dropzone ${dragOver ? 'dragover' : ''}`}
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={(e) => {
                  e.preventDefault();
                  setDragOver(false);
                  if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                    handleFileSelect(e.dataTransfer.files[0]);
                  }
                }}
                onClick={() => fileInputRef.current?.click()}
              >
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  style={{ display: 'none' }} 
                  accept="image/jpeg,image/png,image/jpg"
                  onChange={(e) => handleFileSelect(e.target.files?.[0])}
                />
                <div className="upload-icon-circle">
                  <Upload size={32} />
                </div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Tải ảnh thẻ lên để kiểm tra</h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  Kéo thả ảnh vào đây hoặc bấm để chọn file (JPG, PNG)
                </p>
                <div style={{ display: 'flex', gap: '10px', marginTop: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
                  <button className="btn-upload" onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }}>
                    <Upload size={16} /> Chọn ảnh từ máy
                  </button>
                  <button 
                    className="btn-upload" 
                    style={{ background: 'linear-gradient(135deg, #7c3aed, #4f46e5)', border: '1px solid rgba(139,92,246,0.5)' }}
                    onClick={(e) => { e.stopPropagation(); openCamera(); }}
                  >
                    <Camera size={16} /> Chụp từ webcam
                  </button>
                </div>
              </div>

            ) : (
              <div>
                {/* Visual Tabs */}
                <div className="view-tabs">
                  <button 
                    className={`tab-btn ${activeTab === 'original' ? 'active' : ''}`}
                    onClick={() => setActiveTab('original')}
                  >
                    Ảnh gốc
                  </button>
                  <button 
                    className={`tab-btn ${activeTab === 'face_bbox' ? 'active' : ''}`}
                    onClick={() => setActiveTab('face_bbox')}
                  >
                    <User size={14} /> Khung mặt
                  </button>
                  <button 
                    className={`tab-btn ${activeTab === 'clahe_enhanced' ? 'active' : ''}`}
                    onClick={() => setActiveTab('clahe_enhanced')}
                    style={{ borderColor: activeTab === 'clahe_enhanced' ? '#10b981' : 'rgba(16,185,129,0.3)', color: activeTab === 'clahe_enhanced' ? '#fff' : '#34d399' }}
                  >
                    <Sparkles size={14} /> Làm mịn & Tăng nét DIP
                  </button>
                  <button 
                    className={`tab-btn ${activeTab === 'grayscale' ? 'active' : ''}`}
                    onClick={() => setActiveTab('grayscale')}
                  >
                    Ảnh xám
                  </button>
                </div>

                {/* Viewport */}
                <div className="canvas-viewport">
                  {loading ? (
                    <div style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>
                      <div className="score-number" style={{ fontSize: '1.2rem', color: '#60a5fa' }}>Đang phân tích ảnh của bạn...</div>
                      <p style={{ fontSize: '0.8rem', marginTop: '6px', color: 'var(--text-muted)' }}>Hệ thống đang kiểm tra độ sáng, màu sắc và phổ màu so với ảnh thẻ chuẩn</p>
                    </div>
                  ) : (
                    <img 
                      src={getActiveImageSrc()} 
                      alt="Processing View" 
                      className="canvas-image"
                    />
                  )}
                </div>



                {/* Chú thích khi xem tab Làm mịn & Tăng nét DIP */}
                {activeTab === 'clahe_enhanced' && (
                  <div className="clahe-banner" style={{ background: 'rgba(16,185,129,0.12)', borderColor: 'rgba(16,185,129,0.35)', color: '#6ee7b7' }}>
                    <span>✨ Đã áp dụng bộ lọc song phương Bilateral Filter (làm mịn da bảo toàn biên) kết hợp Unsharp Masking (làm nét chi tiết mắt, tóc) chuẩn giáo trình XLA.</span>
                    <button 
                      className="tab-btn" 
                      style={{ padding: '4px 8px', fontSize: '0.75rem', background: '#10b981', color: '#000', fontWeight: 600 }}
                      onClick={() => setActiveTab('original')}
                    >
                      So với ảnh gốc
                    </button>
                  </div>
                )}


                {/* Re-upload button & Resolution */}
                <div style={{ marginTop: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
                  <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                    <button 
                      className="tab-btn" 
                      style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-primary)', padding: '5px 10px', fontSize: '0.78rem' }}
                      onClick={() => {
                        setPreviewUrl(null);
                        setResult(null);
                        setSelectedFile(null);
                      }}
                    >
                      <RotateCcw size={13} /> Tải ảnh khác
                    </button>
                    <button
                      className="tab-btn"
                      style={{ background: 'rgba(124,58,237,0.15)', color: '#a78bfa', borderColor: 'rgba(139,92,246,0.4)', padding: '5px 10px', fontSize: '0.78rem' }}
                      onClick={() => { setPreviewUrl(null); setResult(null); setSelectedFile(null); setTimeout(openCamera, 50); }}
                    >
                      <Camera size={13} /> Chụp webcam
                    </button>
                  </div>
                  {result && (
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                      Độ phân giải: <strong style={{ color: '#e2e8f0' }}>{result.checks.image_size.width}×{result.checks.image_size.height}</strong> px
                    </span>
                  )}
                </div>

                {/* PHÒNG THÍ NGHIỆM ĐẶC TRƯNG TOÀN CỤC (GLOBAL FEATURES LAB) */}
                {result?.checks?.brightness && (
                  <div className="global-lab-card">
                    <div className="global-lab-header">
                      <div className="global-lab-title" style={{ fontSize: '0.84rem' }}>
                        <BarChart2 size={16} /> Đặc trưng Toàn cục (Global Lab)
                      </div>
                      <span className="crit-val-badge" style={{ color: '#60a5fa', borderColor: 'rgba(96,165,250,0.3)', whiteSpace: 'nowrap' }}>
                        Vector 18-D (Ch.6)
                      </span>
                    </div>

                    {/* 4 Cards chỉ số — viết theo ngôn ngữ dễ hiểu */}
                    <div className="global-metrics-grid">
                      <div className="global-metric-box">
                        <div className="global-metric-label">🌤️ Độ sáng TB</div>
                        <div className="global-metric-val">{result.checks.brightness.mean_intensity}</div>
                        <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                          {result.checks.brightness.mean_intensity < 90 ? '⚠ Hơi tối' : result.checks.brightness.mean_intensity > 215 ? '⚠ Quá sáng' : '✓ Vừa phải'}
                        </div>
                      </div>
                      <div className="global-metric-box">
                        <div className="global-metric-label">🎨 Độ tương phản</div>
                        <div className="global-metric-val">{result.checks.brightness.contrast_std}</div>
                        <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '2px' }}>Độ phong phú màu</div>
                      </div>
                      <div className="global-metric-box">
                        <div className="global-metric-label">⚖️ Lệch sáng</div>
                        <div className="global-metric-val" style={{ color: result.checks.brightness.skewness < 0 ? '#60a5fa' : '#f87171' }}>
                          {result.checks.brightness.skewness > 0 ? `+${result.checks.brightness.skewness}` : result.checks.brightness.skewness}
                        </div>
                        <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                          {result.checks.brightness.skewness > 0.5 ? '← Vùng tối' : result.checks.brightness.skewness < -0.5 ? '→ Vùng sáng' : '≈ Cân bằng'}
                        </div>
                      </div>
                      <div className="global-metric-box" style={{ borderColor: result.checks.brightness.bhattacharyya_distance <= 0.50 ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)' }}>
                        <div className="global-metric-label">🎯 Khớp phổ chuẩn</div>
                        <div className="global-metric-val" style={{ color: result.checks.brightness.bhattacharyya_distance <= 0.50 ? 'var(--success)' : 'var(--danger)' }}>
                          {result.checks.brightness.bhattacharyya_distance}
                        </div>
                        <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                          {result.checks.brightness.bhattacharyya_distance <= 0.50 ? '✓ Khớp chuẩn' : '✗ Lệch chuẩn'}
                        </div>
                      </div>
                    </div>

                    {/* Biểu đồ kép so sánh 2 ngọn núi Histogram 16 bins */}
                    {result.visual_assets?.histogram_normalized_16 && result.visual_assets?.reference_histogram_16 && (
                      <div className="dual-hist-wrapper">
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '6px', display: 'flex', justifyContent: 'space-between' }}>
                          <span>Biểu đồ màu sắc — ảnh bạn (xanh) vs ảnh thẻ chuẩn (vàng):</span>
                          <span style={{ color: result.checks.brightness.bhattacharyya_distance <= 0.50 ? '#34d399' : '#f87171' }}>
                            {result.checks.brightness.bhattacharyya_distance <= 0.50 ? '✓ Màu sắc rất khớp chuẩn' : '⚠ Màu sắc lệch nhiều so với chuẩn'}
                          </span>
                        </div>
                        <div className="dual-hist-container">
                          {result.visual_assets.histogram_normalized_16.map((val, idx) => {
                            const refVal = result.visual_assets.reference_histogram_16[idx] || 0;
                            const h1 = Math.min(100, Math.max(4, val * 160));
                            const h2 = Math.min(100, Math.max(4, refVal * 160));
                            return (
                              <div key={idx} className="dual-hist-col" title={`Bin ${idx} | Hiện tại: ${(val*100).toFixed(1)}% | Chuẩn: ${(refVal*100).toFixed(1)}%`}>
                                <div className="bar-current" style={{ height: `${h1}%` }} />
                                <div className="bar-ref" style={{ height: `${h2}%` }} />
                              </div>
                            );
                          })}
                        </div>
                        <div className="hist-legend">
                          <div className="legend-item">
                            <div className="legend-dot dot-current" />
                            <span>Ảnh của bạn</span>
                          </div>
                          <div className="legend-item">
                            <div className="legend-dot dot-ref" />
                            <span>Ảnh thẻ chuẩn (mẫu so sánh)</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>


          {/* CỘT PHẢI: KẾT QUẢ ĐÁNH GIÁ & 6 TIÊU CHÍ */}
          <div className="card-glass">
            {!result ? (
              <div style={{ textAlign: 'center', padding: '4rem 1rem', color: 'var(--text-muted)' }}>
                <Layers size={48} style={{ opacity: 0.3, marginBottom: '12px' }} />
                <h3 style={{ fontSize: '1.1rem', color: 'var(--text-secondary)' }}>Chưa có kết quả phân tích</h3>
                <p style={{ fontSize: '0.85rem', marginTop: '6px' }}>
                  Vui lòng tải ảnh thẻ lên ở cột bên trái để hệ thống thực hiện kiểm định 6 tiêu chuẩn chất lượng.
                </p>
              </div>
            ) : (
              <div>
                {/* Verdict Banner */}
                <div className={`verdict-box ${result.verdict.toLowerCase()}`}>
                  <div>
                    <div className="verdict-tag">
                      {result.verdict === 'PASS' ? (
                        <>
                          <CheckCircle2 size={28} /> ẢNH ĐẠT CHUẨN
                        </>
                      ) : result.verdict === 'WARNING' ? (
                        <>
                          <AlertTriangle size={28} /> TẠM ĐẠT CHUẨN
                        </>
                      ) : (
                        <>
                          <XCircle size={28} /> KHÔNG ĐẠT CHUẨN
                        </>
                      )}
                    </div>
                    <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                      {result.summary}
                    </div>
                  </div>
                  <div className="score-circle">
                    <div 
                      className="score-number" 
                      style={{ 
                        color: result.verdict === 'PASS' 
                          ? 'var(--success)' 
                          : result.verdict === 'WARNING' 
                            ? 'var(--warning)' 
                            : 'var(--danger)' 
                      }}
                    >
                      {result.overall_score}
                    </div>
                    <div className="score-label">Điểm chất lượng</div>
                  </div>
                </div>

                {/* NÚT TẢI ẢNH ĐỀ XUẤT CHUẨN 3:4 (JPG) */}
                {result?.visual_assets?.standardized && (
                  <div style={{ marginBottom: '1rem' }}>
                    <button 
                      className="btn-std-primary" 
                      onClick={handleDownloadStandardized}
                      style={{
                        width: '100%',
                        padding: '12px 18px',
                        fontSize: '0.92rem',
                        fontWeight: 700,
                        borderRadius: '10px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '8px',
                        cursor: 'pointer'
                      }}
                      title="Tải ảnh thẻ đã được tự động chuẩn hóa tỷ lệ 3:4 (JPG) về máy tính"
                    >
                      <Download size={17} /> Tải ảnh đề xuất chuẩn 3:4 (JPG)
                    </button>
                  </div>
                )}

                {/* BẢNG CHẤM ĐIỂM CHI TIẾT 6 TIÊU CHUẨN (BỐ CỤC GỐC) */}
                <div className="criteria-summary-box">
                  <div className="criteria-summary-header">
                    <div className="criteria-main-title">
                      📊 BẢNG CHẤM ĐIỂM 6 TIÊU CHUẨN (THANG 100 ĐIỂM)
                    </div>
                    <span 
                      className="criteria-score-pill" 
                      style={{
                        background: result.overall_score >= 50 ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                        color: result.overall_score >= 50 ? '#34d399' : '#f87171',
                        borderColor: result.overall_score >= 50 ? 'rgba(16, 185, 129, 0.4)' : 'rgba(239, 68, 68, 0.4)'
                      }}
                    >
                      Tổng: {result.overall_score} / 100 điểm ({result.overall_score >= 50 ? 'ĐẠT CHUẨN PASS' : 'CHƯA ĐẠT'})
                    </span>
                  </div>
                  <div className="score-formula-hint">
                    💡 <strong>Cách tính điểm:</strong> Kích thước (15đ) + Số người (15đ) + Tỉ lệ mặt (20đ) + Độ nét (15đ) + Ánh sáng (20đ) + Phông nền (15đ) = 100đ. Đạt từ 50đ trở lên là ĐẠT CHUẨN.
                  </div>
                </div>

                <div className="criteria-list">
                  
                  {/* 1. Kích thước & Tỉ lệ (15đ) */}
                  <div className={`criterion-item ${(result.checks.image_size.score_earned > 0) ? 'pass-item' : 'fail-item'}`}>
                    <div className="crit-item-top">
                      <div className="crit-left">
                        <div className={`crit-status-icon ${(result.checks.image_size.score_earned > 0) ? 'pass' : 'fail'}`}>
                          {(result.checks.image_size.score_earned > 0) ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
                        </div>
                        <div className="crit-title">1. 📐 Kích thước & Tỉ lệ</div>
                      </div>
                      <div className={`crit-score-badge ${(result.checks.image_size.score_earned > 0) ? 'pass' : 'fail'}`}>
                        {(result.checks.image_size.score_earned > 0) ? `+${result.checks.image_size.score_earned} / 15 đ (ĐẠT)` : '0 / 15 đ (MẤT 15Đ)'}
                      </div>
                    </div>
                    <div className={`crit-explain-row ${(result.checks.image_size.score_earned > 0) ? 'pass' : 'fail'}`}>
                      {(result.checks.image_size.score_earned > 0) ? (
                        <span>✅ <strong>Điểm đạt:</strong> {result.checks.image_size.friendly_pass || "Đúng tỉ lệ chuẩn 3:4 hoặc 4:6, kích thước sắc nét chuẩn in ấn."}</span>
                      ) : (
                        <span>❌ <strong>Lỗi sai:</strong> {result.checks.image_size.friendly_fail || result.checks.image_size.message}</span>
                      )}
                    </div>
                    <div className="crit-tech-row">
                      <span>Đo đạc: {result.checks.image_size.width}×{result.checks.image_size.height} px · Tỉ lệ: {result.checks.image_size.aspect_ratio || "3:4"}</span>
                      <span>Yêu cầu: Chuẩn 3:4 hoặc 4:6, Min 400×500 px</span>
                    </div>
                  </div>

                  {/* 2. Số lượng khuôn mặt (15đ) */}
                  <div className={`criterion-item ${(result.checks.face_count.score_earned > 0) ? 'pass-item' : 'fail-item'}`}>
                    <div className="crit-item-top">
                      <div className="crit-left">
                        <div className={`crit-status-icon ${(result.checks.face_count.score_earned > 0) ? 'pass' : 'fail'}`}>
                          {(result.checks.face_count.score_earned > 0) ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
                        </div>
                        <div className="crit-title">2. 👤 Số người chụp</div>
                      </div>
                      <div className={`crit-score-badge ${(result.checks.face_count.score_earned > 0) ? 'pass' : 'fail'}`}>
                        {(result.checks.face_count.score_earned > 0) ? `+${result.checks.face_count.score_earned} / 15 đ (ĐẠT)` : '0 / 15 đ (MẤT 15Đ)'}
                      </div>
                    </div>
                    <div className={`crit-explain-row ${(result.checks.face_count.score_earned > 0) ? 'pass' : 'fail'}`}>
                      {(result.checks.face_count.score_earned > 0) ? (
                        <span>✅ <strong>Điểm đạt:</strong> {result.checks.face_count.friendly_pass || "Có đúng 1 người chụp, mắt nhìn thẳng vào ống kính."}</span>
                      ) : (
                        <span>❌ <strong>Lỗi sai:</strong> {result.checks.face_count.friendly_fail || result.checks.face_count.message}</span>
                      )}
                    </div>
                    <div className="crit-tech-row">
                      <span>Nhận diện: Phát hiện {result.checks.face_count.detected_count} khuôn mặt</span>
                      <span>Yêu cầu: Duy nhất 1 người</span>
                    </div>
                  </div>

                  {/* 3. Tỷ lệ chiều cao khuôn mặt (20đ) */}
                  <div className={`criterion-item ${(result.checks.face_height_ratio.score_earned > 0) ? 'pass-item' : 'fail-item'}`}>
                    <div className="crit-item-top">
                      <div className="crit-left">
                        <div className={`crit-status-icon ${(result.checks.face_height_ratio.score_earned > 0) ? 'pass' : 'fail'}`}>
                          {(result.checks.face_height_ratio.score_earned > 0) ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
                        </div>
                        <div className="crit-title">3. 🔍 Tỉ lệ khuôn mặt</div>
                      </div>
                      <div className={`crit-score-badge ${(result.checks.face_height_ratio.score_earned > 0) ? 'pass' : 'fail'}`}>
                        {(result.checks.face_height_ratio.score_earned > 0) ? `+${result.checks.face_height_ratio.score_earned} / 20 đ (ĐẠT)` : '0 / 20 đ (MẤT 20Đ)'}
                      </div>
                    </div>
                    <div className={`crit-explain-row ${(result.checks.face_height_ratio.score_earned > 0) ? 'pass' : 'fail'}`}>
                      {(result.checks.face_height_ratio.score_earned > 0) ? (
                        <span>✅ <strong>Điểm đạt:</strong> {result.checks.face_height_ratio.friendly_pass || "Khuôn mặt chiếm tỷ lệ vừa vặn, chuẩn bố cục ICAO."}</span>
                      ) : (
                        <span>❌ <strong>Lỗi sai:</strong> {result.checks.face_height_ratio.friendly_fail || result.checks.face_height_ratio.message}</span>
                      )}
                    </div>
                    <div className="crit-tech-row">
                      <span>Tỷ lệ mặt thực tế: {(result.checks.face_height_ratio.ratio * 100).toFixed(1)}% chiều cao ảnh</span>
                      <span>Yêu cầu: {((result.checks.face_height_ratio.threshold_min || 0.30) * 100).toFixed(0)}% – {((result.checks.face_height_ratio.threshold_max || 0.70) * 100).toFixed(0)}%</span>
                    </div>
                  </div>

                  {/* 4. Độ rõ nét (15đ) */}
                  <div className={`criterion-item ${(result.checks.sharpness.score_earned > 0) ? 'pass-item' : 'fail-item'}`}>
                    <div className="crit-item-top">
                      <div className="crit-left">
                        <div className={`crit-status-icon ${(result.checks.sharpness.score_earned > 0) ? 'pass' : 'fail'}`}>
                          {(result.checks.sharpness.score_earned > 0) ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
                        </div>
                        <div className="crit-title">4. ⚡ Độ nét chi tiết</div>
                      </div>
                      <div className={`crit-score-badge ${(result.checks.sharpness.score_earned > 0) ? 'pass' : 'fail'}`}>
                        {(result.checks.sharpness.score_earned > 0) ? `+${result.checks.sharpness.score_earned} / 15 đ (ĐẠT)` : '0 / 15 đ (MẤT 15Đ)'}
                      </div>
                    </div>
                    <div className={`crit-explain-row ${(result.checks.sharpness.score_earned > 0) ? 'pass' : 'fail'}`}>
                      {(result.checks.sharpness.score_earned > 0) ? (
                        <span>✅ <strong>Điểm đạt:</strong> {result.checks.sharpness.friendly_pass || "Ảnh rất sắc nét, mắt và tóc nhìn rõ từng sợi."}</span>
                      ) : (
                        <span>❌ <strong>Lỗi sai:</strong> {result.checks.sharpness.friendly_fail || result.checks.sharpness.message}</span>
                      )}
                    </div>
                    <div className="crit-tech-row">
                      <span>Điểm nét Laplacian: {result.checks.sharpness.laplacian_variance}</span>
                      <span>Ngưỡng tối thiểu: 75.0</span>
                    </div>
                  </div>

                  {/* 5. Ánh sáng & Màu sắc tổng thể (20đ) */}
                  <div className={`criterion-item ${(result.checks.brightness.score_earned > 0) ? 'pass-item' : 'fail-item'}`}>
                    <div className="crit-item-top">
                      <div className="crit-left">
                        <div className={`crit-status-icon ${(result.checks.brightness.score_earned > 0) ? 'pass' : 'fail'}`}>
                          {(result.checks.brightness.score_earned > 0) ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
                        </div>
                        <div className="crit-title" style={{ color: (result.checks.brightness.score_earned > 0) ? '#93c5fd' : 'inherit' }}>
                          ★ 5. ☀️ Ánh sáng & Màu sắc
                        </div>
                      </div>
                      <div className={`crit-score-badge ${(result.checks.brightness.score_earned > 0) ? 'pass' : 'fail'}`}>
                        {(result.checks.brightness.score_earned > 0) ? `+${result.checks.brightness.score_earned} / 20 đ (ĐẠT)` : '0 / 20 đ (MẤT 20Đ)'}
                      </div>
                    </div>
                    <div className={`crit-explain-row ${(result.checks.brightness.score_earned > 0) ? 'pass' : 'fail'}`}>
                      {(result.checks.brightness.score_earned > 0) ? (
                        <span>✅ <strong>Điểm đạt:</strong> {result.checks.brightness.friendly_pass || "Ánh sáng hài hòa, khuôn mặt sáng rõ, màu sắc khớp chuẩn."}</span>
                      ) : (
                        <span>❌ <strong>Lỗi sai:</strong> {result.checks.brightness.friendly_fail || result.checks.brightness.message}</span>
                      )}
                    </div>
                    <div className="crit-tech-row">
                      <span>Đo đạc: Độ sáng {result.checks.brightness.mean_intensity} (chuẩn 90–215) · Sai lệch màu Bhattacharyya: {result.checks.brightness.bhattacharyya_distance}</span>
                      <span>Yêu cầu dB ≤ 0.50</span>
                    </div>
                  </div>

                  {/* 6. Phông nền sạch đều (15đ) */}
                  <div className={`criterion-item ${(result.checks.background_uniformity.score_earned > 0) ? 'pass-item' : 'fail-item'}`}>
                    <div className="crit-item-top">
                      <div className="crit-left">
                        <div className={`crit-status-icon ${(result.checks.background_uniformity.score_earned > 0) ? 'pass' : 'fail'}`}>
                          {(result.checks.background_uniformity.score_earned > 0) ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
                        </div>
                        <div className="crit-title">6. 🎨 Phông nền sạch đều</div>
                      </div>
                      <div className={`crit-score-badge ${(result.checks.background_uniformity.score_earned > 0) ? 'pass' : 'fail'}`}>
                        {(result.checks.background_uniformity.score_earned > 0) ? `+${result.checks.background_uniformity.score_earned} / 15 đ (ĐẠT)` : '0 / 15 đ (MẤT 15Đ)'}
                      </div>
                    </div>
                    <div className={`crit-explain-row ${(result.checks.background_uniformity.score_earned > 0) ? 'pass' : 'fail'}`}>
                      {(result.checks.background_uniformity.score_earned > 0) ? (
                        <span>✅ <strong>Điểm đạt:</strong> {result.checks.background_uniformity.friendly_pass || "Phông nền trơn phẳng, sạch bóng, không dính bóng đổ hay hoa văn."}</span>
                      ) : (
                        <span>❌ <strong>Lỗi sai:</strong> {result.checks.background_uniformity.friendly_fail || result.checks.background_uniformity.message}</span>
                      )}
                    </div>
                    <div className="crit-tech-row">
                      <span>Đo biến thiên màu nền: {result.checks.background_uniformity.avg_std_dev}</span>
                      <span>Yêu cầu tối đa: {result.checks.background_uniformity.threshold_max_std}</span>
                    </div>
                  </div>

                </div>

              </div>
            )}
          </div>

          {/* CỘT 3 (LỀ NGOÀI CÙNG PHÍA PHẢI): ĐÁNH GIÁ & GÓP Ý */}
          <div className="card-glass col-feedback">
            {!result ? (
              <div style={{ textAlign: 'center', padding: '3.5rem 1rem', color: 'var(--text-muted)' }}>
                <Lightbulb size={40} style={{ opacity: 0.3, marginBottom: '12px' }} />
                <h3 style={{ fontSize: '1rem', color: 'var(--text-secondary)' }}>Đánh giá & Góp ý</h3>
                <p style={{ fontSize: '0.82rem', marginTop: '6px' }}>
                  Các nhận xét chi tiết, chỉ ra điểm đạt, lỗi sai và lời khuyên khắc phục sẽ hiển thị tại đây sau khi phân tích ảnh.
                </p>
              </div>
            ) : (
              <div>
                <div className="feedback-col-header">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Sparkles size={18} style={{ color: '#a855f7' }} />
                    <span style={{ fontWeight: 800, fontSize: '0.95rem', color: '#f1f5f9' }}>
                      ĐÁNH GIÁ & GÓP Ý
                    </span>
                  </div>
                  <span 
                    className="crit-val-badge" 
                    style={{ 
                      color: result.overall_score >= 50 ? '#34d399' : '#f87171', 
                      borderColor: result.overall_score >= 50 ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)',
                      fontSize: '0.72rem'
                    }}
                  >
                    {result.verdict === 'PASS' ? 'ĐẠT CHUẨN' : result.verdict === 'WARNING' ? 'TẠM ĐẠT' : 'KHÔNG ĐẠT'}
                  </span>
                </div>

                <div className="feedback-summary-group" style={{ marginTop: '14px' }}>
                  {/* Danh sách điểm tốt trong ảnh */}
                  {result.good_points && result.good_points.length > 0 && (
                    <div className="good-points-container">
                      <div className="good-points-title">
                        <Sparkles size={16} /> Các điểm tốt ({result.good_points.length} tiêu chí đạt chuẩn):
                      </div>
                      <ul className="good-points-list">
                        {result.good_points.map((gp, i) => (
                          <li key={i}>{gp}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Danh sách lỗi / cần hoàn thiện */}
                  {result.reasons && result.reasons.length > 0 && (
                    <div className="reasons-container">
                      <div className="reasons-title">
                        <AlertTriangle size={16} /> {result.verdict === 'WARNING' ? 'Các điểm cần cải thiện:' : 'Các điểm chưa đạt:'}
                      </div>
                      <ul className="reasons-list">
                        {result.reasons.map((r, i) => (
                          <li key={i}>{r}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Lời khuyên khắc phục */}
                  {result.recommendations && result.recommendations.length > 0 && (
                    <div className="recommendations-container">
                      <div className="recommendations-title">
                        <Lightbulb size={16} /> Lời khuyên khắc phục:
                      </div>
                      <ul className="recommendations-list">
                        {result.recommendations.map((rec, i) => (
                          <li key={i}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

        </div>
      </main>

      {/* WEBCAM MODAL — Fixed portal, always renders on top */}
      {showCamera && (
        <div style={{
          position: 'fixed', inset: 0, zIndex: 1000,
          background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(8px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
          <div style={{
            background: 'var(--surface-primary)', borderRadius: '20px',
            padding: '24px', width: 'min(560px, 95vw)',
            border: '1px solid rgba(139,92,246,0.4)', boxShadow: '0 0 60px rgba(139,92,246,0.3)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#ef4444', animation: 'pulse 1.5s infinite' }} />
                <span style={{ fontWeight: 700, fontSize: '1rem' }}>Camera đang bật — Nhìn thẳng vào ống kính</span>
              </div>
              <button onClick={closeCamera} style={{ background: 'rgba(255,255,255,0.1)', border: 'none', color: '#fff', borderRadius: '8px', padding: '6px', cursor: 'pointer' }}>
                <X size={18} />
              </button>
            </div>
            <div style={{ position: 'relative', borderRadius: '12px', overflow: 'hidden', background: '#000' }}>
              <video ref={videoRef} autoPlay playsInline muted
                style={{ width: '100%', display: 'block', transform: 'scaleX(-1)', maxHeight: '360px', objectFit: 'cover' }}
              />
              <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', pointerEvents: 'none' }}>
                <div style={{ width: '160px', height: '200px', border: '2px dashed rgba(139,92,246,0.8)', borderRadius: '50% 50% 45% 45%' }} />
              </div>
              {countdown !== null && (
                <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.5)' }}>
                  <span style={{ fontSize: countdown === '📸' ? '4rem' : '6rem', fontWeight: 900, color: '#fff', textShadow: '0 0 30px rgba(139,92,246,0.9)' }}>
                    {countdown}
                  </span>
                </div>
              )}
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textAlign: 'center', margin: '12px 0 8px' }}>
              💡 Đặt khuôn mặt vào trong khung oval · Nhìn thẳng · Phông nền sáng đều
            </p>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                onClick={capturePhoto}
                disabled={!cameraReady || countdown !== null}
                style={{
                  flex: 1, padding: '12px', borderRadius: '10px', fontWeight: 700, fontSize: '1rem', cursor: 'pointer',
                  background: cameraReady && countdown === null ? 'linear-gradient(135deg, #7c3aed, #4f46e5)' : 'rgba(255,255,255,0.1)',
                  color: '#fff', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px'
                }}
              >
                <Aperture size={20} />
                {!cameraReady ? 'Đang khởi động camera...' : countdown !== null ? 'Đang chụp...' : '📸 Chụp ảnh (tự đếm ngược 3 giây)'}
              </button>
              <button onClick={closeCamera} style={{ padding: '12px 16px', borderRadius: '10px', background: 'rgba(239,68,68,0.2)', color: '#f87171', border: '1px solid rgba(239,68,68,0.3)', cursor: 'pointer', fontWeight: 600 }}>
                Hủy
              </button>
            </div>
          </div>
          <canvas ref={canvasRef} style={{ display: 'none' }} />
        </div>
      )}
    </div>
  );
}


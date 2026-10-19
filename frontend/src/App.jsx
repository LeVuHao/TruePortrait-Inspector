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
  Wand2,
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
      case 'standardized':
        return result.visual_assets.standardized || previewUrl;
      case 'grayscale':
        return result.visual_assets.grayscale || previewUrl;
      case 'laplacian_map':
        return result.visual_assets.laplacian_map || previewUrl;
      case 'background_rois':
        return result.visual_assets.background_rois || previewUrl;
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
            <span>Preset: STANDARD_ID_PHOTO (3:4, Min 600x800)</span>
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
                    style={{ borderColor: activeTab === 'clahe_enhanced' ? '#f59e0b' : 'rgba(245,158,11,0.3)', color: activeTab === 'clahe_enhanced' ? '#fff' : '#fbbf24' }}
                  >
                    <Sparkles size={14} /> Cân bằng CLAHE
                  </button>
                  <button 
                    className={`tab-btn tab-standardized ${activeTab === 'standardized' ? 'active' : ''}`}
                    onClick={() => setActiveTab('standardized')}
                  >
                    <Wand2 size={14} /> Chuẩn hóa DIP (3:4)
                  </button>
                  <button 
                    className={`tab-btn ${activeTab === 'grayscale' ? 'active' : ''}`}
                    onClick={() => setActiveTab('grayscale')}
                  >
                    Ảnh xám
                  </button>
                  <button 
                    className={`tab-btn ${activeTab === 'laplacian_map' ? 'active' : ''}`}
                    onClick={() => setActiveTab('laplacian_map')}
                  >
                    <Zap size={14} /> Viền Laplacian
                  </button>
                  <button 
                    className={`tab-btn ${activeTab === 'background_rois' ? 'active' : ''}`}
                    onClick={() => setActiveTab('background_rois')}
                  >
                    <Maximize2 size={14} /> 4 Góc ROI
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

                {/* Chú thích Ảnh đề xuất khi đang xem tab standardized */}
                {activeTab === 'standardized' && (
                  <div className="standardized-banner">
                    <div className="std-banner-info">
                      <Wand2 size={16} />
                      <span>
                        Ảnh đề xuất hiệu chỉnh: Tỷ lệ 3:4 ({result?.standardization_report?.standardized_width}x{result?.standardization_report?.standardized_height} px) theo đúng lỗi thực tế của ảnh (không can thiệp thừa).
                      </span>
                    </div>
                    <div className="std-banner-actions">
                      <button className="btn-std-download" onClick={handleDownloadStandardized}>
                        <Download size={13} /> Tải ảnh đề xuất (JPG)
                      </button>
                    </div>
                  </div>
                )}


                {/* Chú thích CLAHE khi đang xem tab CLAHE */}
                {activeTab === 'clahe_enhanced' && (
                  <div className="clahe-banner">
                    <span>✨ Ảnh đã được tự động cân bằng sáng bằng thuật toán CLAHE trên không gian màu CIELAB.</span>
                    <button 
                      className="tab-btn" 
                      style={{ padding: '4px 8px', fontSize: '0.75rem', background: '#f59e0b', color: '#000' }}
                      onClick={() => setActiveTab('original')}
                    >
                      So với ảnh gốc
                    </button>
                  </div>
                )}


                {/* Re-upload button */}
                <div style={{ marginTop: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button 
                      className="tab-btn" 
                      style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-primary)' }}
                      onClick={() => {
                        setPreviewUrl(null);
                        setResult(null);
                        setSelectedFile(null);
                      }}
                    >
                      <RotateCcw size={14} /> Tải ảnh khác
                    </button>
                    <button
                      className="tab-btn"
                      style={{ background: 'rgba(124,58,237,0.15)', color: '#a78bfa', borderColor: 'rgba(139,92,246,0.4)' }}
                      onClick={() => { setPreviewUrl(null); setResult(null); setSelectedFile(null); setTimeout(openCamera, 50); }}
                    >
                      <Camera size={14} /> Chụp lại webcam
                    </button>
                  </div>
                  {result && (
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Độ phân giải: {result.checks.image_size.width}x{result.checks.image_size.height} px
                    </span>
                  )}
                </div>

                {/* PHÒNG THÍ NGHIỆM ĐẶC TRƯNG TOÀN CỤC (GLOBAL FEATURES LAB) */}
                {result?.checks?.brightness && (
                  <div className="global-lab-card">
                    <div className="global-lab-header">
                      <div className="global-lab-title">
                        <BarChart2 size={16} /> Chuyên đề: Trích xuất Đặc trưng Toàn cục (Global Features Lab)
                      </div>
                      <span className="crit-val-badge" style={{ color: '#60a5fa', borderColor: 'rgba(96,165,250,0.3)' }}>
                        Vector 18-D (Ch.6 DIP)
                      </span>
                    </div>

                    {/* 4 Cards chỉ số — viết theo ngôn ngữ dễ hiểu */}
                    <div className="global-metrics-grid">
                      <div className="global-metric-box">
                        <div className="global-metric-label">🌤️ Độ sáng trung bình</div>
                        <div className="global-metric-val">{result.checks.brightness.mean_intensity}</div>
                        <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                          {result.checks.brightness.mean_intensity < 90 ? '⚠ Ảnh hơi tối' : result.checks.brightness.mean_intensity > 215 ? '⚠ Ảnh quá sáng' : '✓ Sáng vừa phải'}
                        </div>
                      </div>
                      <div className="global-metric-box">
                        <div className="global-metric-label">🎨 Độ tương phản màu</div>
                        <div className="global-metric-val">{result.checks.brightness.contrast_std}</div>
                        <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '2px' }}>Màu sắc đa dạng hay đơn điệu</div>
                      </div>
                      <div className="global-metric-box">
                        <div className="global-metric-label">⚖️ Sáng lệch về phía</div>
                        <div className="global-metric-val" style={{ color: result.checks.brightness.skewness < 0 ? '#60a5fa' : '#f87171' }}>
                          {result.checks.brightness.skewness > 0 ? `+${result.checks.brightness.skewness}` : result.checks.brightness.skewness}
                        </div>
                        <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                          {result.checks.brightness.skewness < -0.5 ? '← Lệch về vùng tối' : result.checks.brightness.skewness > 0.5 ? '→ Lệch về vùng sáng' : '≈ Cân bằng'}
                        </div>
                      </div>
                      <div className="global-metric-box" style={{ borderColor: result.checks.brightness.bhattacharyya_distance < 0.45 ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)' }}>
                        <div className="global-metric-label">🎯 Phổ màu khớp chuẩn?</div>
                        <div className="global-metric-val" style={{ color: result.checks.brightness.bhattacharyya_distance < 0.45 ? 'var(--success)' : 'var(--danger)' }}>
                          {result.checks.brightness.bhattacharyya_distance}
                        </div>
                        <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                          {result.checks.brightness.bhattacharyya_distance < 0.45 ? '✓ Rất giống ảnh chuẩn' : '✗ Khác nhiều so với chuẩn'}
                        </div>
                      </div>
                    </div>

                    {/* Biểu đồ kép so sánh 2 ngọn núi Histogram 16 bins */}
                    {result.visual_assets?.histogram_normalized_16 && result.visual_assets?.reference_histogram_16 && (
                      <div className="dual-hist-wrapper">
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '6px', display: 'flex', justifyContent: 'space-between' }}>
                          <span>Biểu đồ màu sắc — ảnh bạn (xanh) vs ảnh thẻ chuẩn (vàng):</span>
                          <span style={{ color: result.checks.brightness.bhattacharyya_distance < 0.45 ? '#34d399' : '#f87171' }}>
                            {result.checks.brightness.bhattacharyya_distance < 0.45 ? '✓ Màu sắc rất khớp chuẩn' : '⚠ Màu sắc lệch nhiều so với chuẩn'}
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

                {/* KHỐI XUẤT ẢNH CHUẨN HÓA DIP (AUTO-STANDARDIZER ACTION CARD) */}
                {result?.visual_assets?.standardized && (
                  <div className="auto-standardize-card">
                    <div className="std-card-header">
                      <div className="std-header-left">
                        <div className="std-badge-icon">
                          <Wand2 size={18} />
                        </div>
                        <div>
                          <div className="std-card-title">Ảnh Đề Xuất Hiệu Chỉnh (Targeted DIP Fix)</div>
                          <div className="std-card-sub">Tự động sửa đúng lỗi: giảm chói, nâng sáng hoặc căn lại khung 3:4</div>
                        </div>
                      </div>
                      <span className="std-pill">Adaptive Fix</span>
                    </div>

                    {/* 4 Chỉ số chuẩn hóa */}
                    <div className="std-highlights-grid">
                      <div className="std-hl-item">
                        <div className="std-hl-label">Bố cục & Kích thước</div>
                        <div className="std-hl-val">3:4 ({result.standardization_report?.standardized_width}x{result.standardization_report?.standardized_height} px)</div>
                      </div>
                      <div className="std-hl-item">
                        <div className="std-hl-label">Tỷ lệ mặt (Face)</div>
                        <div className="std-hl-val">~54% (Chuẩn ICAO)</div>
                      </div>
                      <div className="std-hl-item">
                        <div className="std-hl-label">Cân bằng sáng</div>
                        <div className="std-hl-val">Thích nghi theo lỗi</div>
                      </div>
                      <div className="std-hl-item">
                        <div className="std-hl-label">Độ nét chi tiết</div>
                        <div className="std-hl-val">Bảo toàn tự nhiên</div>
                      </div>
                    </div>

                    {/* Nút hành động chính */}
                    <div className="std-card-actions">
                      <button 
                        className="btn-std-primary" 
                        onClick={handleDownloadStandardized}
                        title="Tải ảnh đã hiệu chỉnh theo đúng tiêu chuẩn về máy tính"
                      >
                        <Download size={15} /> Tải ảnh đề xuất (JPG)
                      </button>
                      <button 
                        className="btn-std-secondary" 
                        onClick={() => setActiveTab('standardized')}
                        title="Chuyển sang xem ảnh đề xuất trên Canvas"
                      >
                        <Wand2 size={15} /> Xem trên Canvas
                      </button>
                    </div>

                    {/* Nhận xét sơ qua về khung ảnh & bố cục */}
                    <div className="std-overview-box">
                      <div className="std-overview-title">
                        <Camera size={15} /> Nhận xét sơ bộ về khung ảnh:
                      </div>
                      <div className="std-overview-points">
                        {result?.standardization_report?.framing_notes && result.standardization_report.framing_notes.length > 0 ? (
                          result.standardization_report.framing_notes.map((note, i) => (
                            <div key={i} className="std-point-row">
                              <span className="std-point-dot">●</span>
                              <span>{note}</span>
                            </div>
                          ))
                        ) : (
                          <>
                            <div className="std-point-row">
                              <span className="std-point-dot">●</span>
                              <span>Khung hình đã được căn chỉnh theo chuẩn tỷ lệ 3:4 ({result.standardization_report?.standardized_width}x{result.standardization_report?.standardized_height} px), khuôn mặt nằm ở vị trí trung tâm ngay ngắn.</span>
                            </div>
                            <div className="std-point-row">
                              <span className="std-point-dot">●</span>
                              <span>Tỷ lệ chiều cao khuôn mặt chiếm ~54% khung hình, khoảng thở đỉnh đầu và hai bên vai cân đối chuẩn ảnh thẻ ICAO.</span>
                            </div>
                            <div className="std-point-row">
                              <span className="std-point-dot">●</span>
                              <span>Màu sắc và ánh sáng tổng thể được bảo toàn tự nhiên, sẵn sàng in ấn hoặc dán hồ sơ.</span>
                            </div>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Danh sách 6 tiêu chí chi tiết */}
                <h4 style={{ fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '0.5px', color: 'var(--text-muted)', marginBottom: '10px' }}>
                  Chi tiết 6 tiêu chuẩn kiểm định (DIP Rules):
                </h4>

                <div className="criteria-list">
                  
                  {/* 1. Kích thước & Tỉ lệ */}
                  <div className="criterion-item">
                    <div className="crit-left">
                      <div className={`crit-status-icon ${result.checks.image_size.passed ? 'pass' : 'fail'}`}>
                        {result.checks.image_size.passed ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
                      </div>
                      <div>
                        <div className="crit-title">1. 📐 Kích thước & Tỉ lệ ảnh</div>
                        <div className="crit-desc">{result.checks.image_size.message}</div>
                      </div>
                    </div>
                    <div className="crit-val-badge" title="Chiều rộng x Chiều cao và tỉ lệ">
                      {result.checks.image_size.width}×{result.checks.image_size.height} px
                    </div>
                  </div>

                  {/* 2. Số lượng khuôn mặt */}
                  <div className="criterion-item">
                    <div className="crit-left">
                      <div className={`crit-status-icon ${result.checks.face_count.passed ? 'pass' : 'fail'}`}>
                        {result.checks.face_count.passed ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
                      </div>
                      <div>
                        <div className="crit-title">2. 👤 Số người trong ảnh</div>
                        <div className="crit-desc">{result.checks.face_count.message}</div>
                      </div>
                    </div>
                    <div className="crit-val-badge">
                      Phát hiện {result.checks.face_count.detected_count} người (yêu cầu: {result.checks.face_count.required_count})
                    </div>
                  </div>

                  {/* 3. Tỷ lệ chiều cao khuôn mặt */}
                  <div className="criterion-item">
                    <div className="crit-left">
                      <div className={`crit-status-icon ${result.checks.face_height_ratio.passed ? 'pass' : 'fail'}`}>
                        {result.checks.face_height_ratio.passed ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
                      </div>
                      <div>
                        <div className="crit-title">3. 🔍 Khuôn mặt chiếm bao nhiêu ảnh?</div>
                        <div className="crit-desc">{result.checks.face_height_ratio.message}</div>
                      </div>
                    </div>
                    <div className="crit-val-badge" title="Tỉ lệ chiều cao mặt/chiều cao ảnh">
                      Mặt chiếm {(result.checks.face_height_ratio.ratio * 100).toFixed(1)}% ảnh (yêu cầu {result.checks.face_height_ratio.threshold_min * 100}%–{result.checks.face_height_ratio.threshold_max * 100}%)
                    </div>
                  </div>

                  {/* 4. Độ rõ nét (Sharpness / Laplacian) */}
                  <div className="criterion-item">
                    <div className="crit-left">
                      <div className={`crit-status-icon ${result.checks.sharpness.passed ? 'pass' : 'fail'}`}>
                        {result.checks.sharpness.passed ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
                      </div>
                      <div>
                        <div className="crit-title">4. 🔎 Ảnh có rõ nét không?</div>
                        <div className="crit-desc">{result.checks.sharpness.message}</div>
                      </div>
                    </div>
                    <div className="crit-val-badge" title="Điểm nét càng cao càng rõ. Dưới ngưỡng tối thiểu = ảnh mờ">
                      Điểm nét: {result.checks.sharpness.laplacian_variance} / min {result.checks.sharpness.threshold_min}
                    </div>
                  </div>

                  {/* 5. Đặc trưng Toàn cục (Global Photometric & Optical Quality) */}
                  <div className="criterion-item" style={{ borderColor: result.checks.brightness.passed ? 'rgba(59,130,246,0.4)' : 'rgba(239,68,68,0.4)', background: 'rgba(59,130,246,0.06)' }}>
                    <div className="crit-left">
                      <div className={`crit-status-icon ${result.checks.brightness.passed ? 'pass' : 'fail'}`}>
                        {result.checks.brightness.passed ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
                      </div>
                      <div>
                        <div className="crit-title" style={{ color: '#93c5fd' }}>
                          ★ 5. ☀️ Ánh sáng & Màu sắc tổng thể
                        </div>
                        <div className="crit-desc">{result.checks.brightness.message}</div>
                      </div>
                    </div>
                    <div className="crit-val-badge" style={{ color: result.checks.brightness.passed ? '#34d399' : '#f87171' }} title="Độ khớp phổ màu với ảnh thẻ chuẩn — càng thấp càng tốt">
                      {result.checks.brightness.optical_label || 'Đạt chuẩn'} — màu sắc khớp {Math.round((1 - Math.min(result.checks.brightness.bhattacharyya_distance, 1)) * 100)}%
                    </div>
                  </div>

                  {/* 6. Độ đồng nhất nền */}
                  <div className="criterion-item">
                    <div className="crit-left">
                      <div className={`crit-status-icon ${result.checks.background_uniformity.passed ? 'pass' : 'fail'}`}>
                        {result.checks.background_uniformity.passed ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
                      </div>
                      <div>
                        <div className="crit-title">6. 🖼️ Phông nền có sạch không?</div>
                        <div className="crit-desc">{result.checks.background_uniformity.message}</div>
                      </div>
                    </div>
                    <div className="crit-val-badge" title="Độ loang lổ nền: càng thấp càng đồng màu. Vượt ngưỡng = nền không đều">
                      Độ loang lổ: {result.checks.background_uniformity.avg_std_dev} / max {result.checks.background_uniformity.threshold_max_std}
                    </div>
                  </div>

                </div>

                {/* Danh sách điểm tốt trong ảnh */}
                {result.good_points && result.good_points.length > 0 && (
                  <div className="good-points-container">
                    <div className="good-points-title">
                      <Sparkles size={16} /> Các điểm tốt trong ảnh ({result.good_points.length} tiêu chí đạt chuẩn):
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


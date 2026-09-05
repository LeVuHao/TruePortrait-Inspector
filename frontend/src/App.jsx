import React, { useState, useRef } from 'react';
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
  Sparkles
} from 'lucide-react';

export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState('original');
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (file) => {
    if (!file) return;
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
    analyzeImage(file);
  };

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

  const getActiveImageSrc = () => {
    if (!result || !result.visual_assets) return previewUrl;
    switch (activeTab) {
      case 'original':
        return result.visual_assets.original || previewUrl;
      case 'face_bbox':
        return result.visual_assets.face_bbox || previewUrl;
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
            <p className="brand-subtitle">Hệ thống kiểm tra chất lượng ảnh thẻ tự động (DIP Core)</p>
          </div>
        </div>
        <div className="header-controls">
          <div className="preset-badge">
            <Square size={14} />
            <span>Chuẩn: STANDARD_ID_PHOTO (3:4, Min 600x800)</span>
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
                <button className="btn-upload" style={{ marginTop: '8px' }}>
                  <Upload size={16} /> Chọn ảnh từ máy
                </button>
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
                    <User size={14} /> Phát hiện mặt
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
                    <Zap size={14} /> Cạnh viền Laplacian
                  </button>
                  <button 
                    className={`tab-btn ${activeTab === 'background_rois' ? 'active' : ''}`}
                    onClick={() => setActiveTab('background_rois')}
                  >
                    <Maximize2 size={14} /> 4 Góc ROI Nền
                  </button>
                </div>

                {/* Viewport */}
                <div className="canvas-viewport">
                  {loading ? (
                    <div style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>
                      <div className="score-number" style={{ fontSize: '1.2rem', color: '#60a5fa' }}>Đang chạy Image Processing Pipeline...</div>
                      <p style={{ fontSize: '0.8rem', marginTop: '6px', color: 'var(--text-muted)' }}>Tính toán Laplacian, Histogram & 4 góc nền ROI</p>
                    </div>
                  ) : (
                    <img 
                      src={getActiveImageSrc()} 
                      alt="Processing View" 
                      className="canvas-image"
                    />
                  )}
                </div>

                {/* Re-upload button */}
                <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
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
                  {result && (
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Độ phân giải: {result.checks.image_size.width}x{result.checks.image_size.height} px
                    </span>
                  )}
                </div>

                {/* Histogram Visualizer nếu có dữ liệu */}
                {result?.visual_assets?.histogram_data && (
                  <div style={{ marginTop: '1.2rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                      <BarChart2 size={15} /> Biểu đồ phân bố cường độ sáng (Brightness Histogram - 16 bins):
                    </div>
                    <div className="histogram-container">
                      {result.visual_assets.histogram_data.map((val, idx) => {
                        const maxVal = Math.max(...result.visual_assets.histogram_data, 1);
                        const heightPct = Math.max(8, (val / maxVal) * 100);
                        return (
                          <div 
                            key={idx} 
                            className="hist-bar" 
                            style={{ height: `${heightPct}%` }}
                            title={`Bin ${idx}: ${val} pixels`}
                          />
                        );
                      })}
                    </div>
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
                    <div className="score-number" style={{ color: result.verdict === 'PASS' ? 'var(--success)' : 'var(--danger)' }}>
                      {result.overall_score}
                    </div>
                    <div className="score-label">Điểm chất lượng</div>
                  </div>
                </div>

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
                        <div className="crit-title">1. Kích thước & Tỉ lệ khung hình</div>
                        <div className="crit-desc">{result.checks.image_size.message}</div>
                      </div>
                    </div>
                    <div className="crit-val-badge">
                      {result.checks.image_size.width}x{result.checks.image_size.height} | {result.checks.image_size.aspect_ratio}
                    </div>
                  </div>

                  {/* 2. Số lượng khuôn mặt */}
                  <div className="criterion-item">
                    <div className="crit-left">
                      <div className={`crit-status-icon ${result.checks.face_count.passed ? 'pass' : 'fail'}`}>
                        {result.checks.face_count.passed ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
                      </div>
                      <div>
                        <div className="crit-title">2. Số lượng khuôn mặt</div>
                        <div className="crit-desc">{result.checks.face_count.message}</div>
                      </div>
                    </div>
                    <div className="crit-val-badge">
                      {result.checks.face_count.detected_count} / {result.checks.face_count.required_count} mặt
                    </div>
                  </div>

                  {/* 3. Tỷ lệ chiều cao khuôn mặt */}
                  <div className="criterion-item">
                    <div className="crit-left">
                      <div className={`crit-status-icon ${result.checks.face_height_ratio.passed ? 'pass' : 'fail'}`}>
                        {result.checks.face_height_ratio.passed ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
                      </div>
                      <div>
                        <div className="crit-title">3. Tỷ lệ chiều cao khuôn mặt (Face Height Ratio)</div>
                        <div className="crit-desc">{result.checks.face_height_ratio.message}</div>
                      </div>
                    </div>
                    <div className="crit-val-badge">
                      {(result.checks.face_height_ratio.ratio * 100).toFixed(1)}% ({result.checks.face_height_ratio.threshold_min * 100}% - {result.checks.face_height_ratio.threshold_max * 100}%)
                    </div>
                  </div>

                  {/* 4. Độ rõ nét (Sharpness / Laplacian) */}
                  <div className="criterion-item">
                    <div className="crit-left">
                      <div className={`crit-status-icon ${result.checks.sharpness.passed ? 'pass' : 'fail'}`}>
                        {result.checks.sharpness.passed ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
                      </div>
                      <div>
                        <div className="crit-title">4. Độ rõ nét (Phương sai Laplacian)</div>
                        <div className="crit-desc">{result.checks.sharpness.message}</div>
                      </div>
                    </div>
                    <div className="crit-val-badge">
                      Var: {result.checks.sharpness.laplacian_variance} (Min {result.checks.sharpness.threshold_min})
                    </div>
                  </div>

                  {/* 5. Độ sáng & Độ tương phản */}
                  <div className="criterion-item">
                    <div className="crit-left">
                      <div className={`crit-status-icon ${result.checks.brightness.passed ? 'pass' : 'fail'}`}>
                        {result.checks.brightness.passed ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
                      </div>
                      <div>
                        <div className="crit-title">5. Độ sáng & Độ tương phản</div>
                        <div className="crit-desc">{result.checks.brightness.message}</div>
                      </div>
                    </div>
                    <div className="crit-val-badge">
                      Mean: {result.checks.brightness.mean_intensity} | Std: {result.checks.brightness.contrast_std}
                    </div>
                  </div>

                  {/* 6. Độ đồng nhất nền */}
                  <div className="criterion-item">
                    <div className="crit-left">
                      <div className={`crit-status-icon ${result.checks.background_uniformity.passed ? 'pass' : 'fail'}`}>
                        {result.checks.background_uniformity.passed ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
                      </div>
                      <div>
                        <div className="crit-title">6. Độ đồng nhất phông nền (4 góc ROI)</div>
                        <div className="crit-desc">{result.checks.background_uniformity.message}</div>
                      </div>
                    </div>
                    <div className="crit-val-badge">
                      Std 4 góc: {result.checks.background_uniformity.avg_std_dev} (Max {result.checks.background_uniformity.threshold_max_std})
                    </div>
                  </div>

                </div>

                {/* Danh sách lỗi và lời khuyên */}
                {result.reasons && result.reasons.length > 0 && (
                  <div className="reasons-container">
                    <div className="reasons-title">
                      <AlertTriangle size={16} /> Các điểm cần khắc phục:
                    </div>
                    <ul className="reasons-list">
                      {result.reasons.map((r, i) => (
                        <li key={i}>{r}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>

        </div>
      </main>
    </div>
  );
}

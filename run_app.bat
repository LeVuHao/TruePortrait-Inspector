@echo off
title PhotoCheck - Khoi dong he thong tu dong
color 0B

echo ===================================================================
echo   PHOTOCHECK -- HE THONG KIEM DINH CHAT LUONG ANH THE TU DONG
echo   Chuyen de: Trich xuat Dac trung Toan cuc (Global Features)
echo   Nhom thuc hien: Le Vu Hao (Leader), Quan, Chuong, Huy
echo ===================================================================
echo.

echo [*] Dang khoi dong Backend FastAPI (Port 8000)...
start "PhotoCheck Backend (FastAPI)" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --port 8000 --reload"

echo [*] Dang khoi dong Frontend React Web Dashboard (Port 5173)...
start "PhotoCheck Frontend (React)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo [*] Dang cho cac server san sang trong 3 giay...
timeout /t 3 /nobreak >nul

echo [*] Dang mo trinh duyet Web tai http://localhost:5173...
start http://localhost:5173

echo.
echo ===================================================================
echo   HE THONG DA KHOI DONG THANH CONG!
echo   - Backend API : http://127.0.0.1:8000/docs
echo   - Web Demo    : http://localhost:5173
echo   - Anh mau demo: %~dp0demo_samples\
echo ===================================================================
echo.
echo Nhan phim bat ky de dong cua so khoi dong nay (hai server van chay)...
pause >nul

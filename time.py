<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Xem Giờ Online</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1f4068, #162447);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: #ffffff;
        }

        .clock-container {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 40px 60px;
            border-radius: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            text-align: center;
        }

        .date {
            font-size: 1.2rem;
            letter-spacing: 2px;
            color: #e4e4e4;
            margin-bottom: 15px;
            text-transform: uppercase;
        }

        .time {
            font-size: 4.5rem;
            font-weight: 700;
            letter-spacing: 3px;
            color: #00adb5;
            text-shadow: 0 0 20px rgba(0, 173, 181, 0.5);
        }

        .session {
            font-size: 1.5rem;
            margin-left: 10px;
            color: #ff5722;
            font-weight: bold;
        }
    </style>
</head>
<body>

    <div class="clock-container">
        <div class="date" id="date-box">Đang tải ngày...</div>
        <div class="time">
            <span id="hours">00</span>:<span id="minutes">00</span>:<span id="seconds">00</span>
            <span class="session" id="session">AM</span>
        </div>
    </div>

    <script>
        function updateClock() {
            const now = new Date();

            // Lấy giờ, phút, giây
            let hours = now.getHours();
            let minutes = now.getMinutes();
            let seconds = now.getSeconds();
            
            // Định dạng 12 giờ (nếu muốn dùng 24h thì bỏ đoạn chuyển đổi AM/PM này)
            let session = "AM";
            if (hours >= 12) {
                session = "PM";
            }
            // hours = hours % 12;
            // hours = hours ? hours : 12; // Giờ '0' sẽ thành '12'

            // Thêm số 0 đằng trước nếu nhỏ hơn 10
            hours = hours < 10 ? "0" + hours : hours;
            minutes = minutes < 10 ? "0" + minutes : minutes;
            seconds = seconds < 10 ? "0" + seconds : seconds;

            // Hiển thị lên giao diện
            document.getElementById("hours").innerText = hours;
            document.getElementById("minutes").innerText = minutes;
            document.getElementById("seconds").innerText = seconds;
            document.getElementById("session").innerText = session;

            // Lấy ngày tháng năm (Định dạng tiếng Việt)
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            const dateString = now.toLocaleDateString('vi-VN', options);
            document.getElementById("date-box").innerText = dateString;
        }

        // Chạy ngay lập tức khi tải trang và lặp lại sau mỗi 1 giây
        setInterval(updateClock, 1000);
        updateClock();
    </script>

</body>
</html>
# Viết code của bạn ở đây
print('Hello from Termux Professional System!')
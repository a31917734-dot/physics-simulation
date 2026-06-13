import tkinter as tk
import math

# --- 1. 대화 내용을 바탕으로 한 정밀 물리 상수 설정 ---
g = 9.8          # 중력 가속도 표준값 (9.8 m/s^2)
m_ball = 0.145   # 야구공 질량 (0.145 kg)
r_ball = 0.037   # 야구공 반지름 (0.037 m)
C_d = 0.3        # 공기 저항 계수 (무차원 수)
rho = 1.2        # 공기 밀도 (1.2 kg/m^3, 20°C 상온 기준)

# --- 2. 공간 및 창문 스펙 설정 ---
PPM = 15         # 화면 비율 (1m = 15픽셀)
WIDTH, HEIGHT = 1350, 750

# 발사 지점: 운동장의 왼쪽 모서리 (바닥에서 1.6m 높이에서 던진다고 가정)
start_x = 50
start_y = HEIGHT - int(1.60 * PPM)       

# 목표 창문 위치 설정 (가로 거리: 57.45m, 높이: 6.0m)
target_x = start_x + int(57.45 * PPM)     
target_y = HEIGHT - int(6.0 * PPM)        

# 창문 크기: 가로 0.5m, 세로 1.5m
window_w = int(0.5 * PPM)
window_h = int(1.5 * PPM)

# --- 3. 게임 상태 및 데이터 변수 ---
v0 = 35.0
angle = 35.0
ball_x, ball_y = float(start_x), float(start_y)
vx, vy = 0.0, 0.0
trail = []
is_flying = False

# 그래프 데이터 배열
time_data = []
height_data = []
vx_data = []
vy_data = []
v_total_data = []
current_time = 0.0

# --- 4. Tkinter 창 설정 ---
root = tk.Tk()
root.title("Physics Simulator (Final Version for Report)")
root.geometry(f"{WIDTH}x{HEIGHT}")
root.resizable(False, False)

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#1e1e1e")
canvas.pack()

# --- 5. 정밀 물리 엔진 연산 (공기 저항 포함) ---
def update_physics():
    global ball_x, ball_y, vx, vy, is_flying, trail, current_time
    
    if not is_flying:
        return

    v_mag = math.sqrt(vx**2 + vy**2)
    
    # 공기 저항력 (F = 0.5 * Cd * rho * A * v^2) 계산
    A = math.pi * (r_ball**2)
    f_drag = 0.5 * C_d * rho * A * (v_mag**2)
    
    ax_drag = -(f_drag * (vx / v_mag)) / m_ball if v_mag > 0 else 0
    ay_drag = -(f_drag * (vy / v_mag)) / m_ball if v_mag > 0 else 0
    
    ax = ax_drag
    ay = g + ay_drag  # 중력가속도 9.8 적용
    
    dt = 1 / 60
    vx += ax * dt
    vy += ay * dt
    
    ball_x += (vx * PPM) * dt
    ball_y += (vy * PPM) * dt
    current_time += dt
    
    h_m = (HEIGHT - ball_y) / PPM
    time_data.append(current_time)
    height_data.append(h_m)
    vx_data.append(vx)
    vy_data.append(-vy)  
    v_total_data.append(v_mag)
    
    trail.append((ball_x, ball_y))
    
    # 바닥 충돌 판정
    if ball_y >= HEIGHT - 10:
        is_flying = False
        draw_scene("FAIL: Hit Ground", (255, 100, 100))
        return
        
    # 창문(벽) 도달 판정
    if ball_x >= target_x:
        is_flying = False
        win_top = target_y - window_h // 2
        win_bottom = target_y + window_h // 2
        
        if win_top <= ball_y <= win_bottom:
            # 수직 충격량 계산 (Ix = m * vx)
            impulse_x = m_ball * vx
            
            # 5mm 유리의 파괴 임계값(1.5 N-s) 적용 판정
            if impulse_x >= 1.5:
                info = f"SUCCESS! WINDOW BROKEN\nImpact V: {v_mag:.2f} m/s | Impulse: {impulse_x:.2f} N-s (>= 1.5)"
                draw_scene(info, (100, 255, 100))
            else:
                info = f"FAIL: Hit Window but NOT Broken\nImpulse: {impulse_x:.2f} N-s (< 1.5 임계값 미달)"
                draw_scene(info, (255, 200, 50))
        else:
            info = f"FAIL: Hit Wall\nHeight: {h_m:.2f}m (Target: 6.0m)"
            draw_scene(info, (255, 150, 50))
        return

    draw_scene()
    root.after(16, update_physics)

# --- 6. 축 및 데이터 드로잉 함수 ---
def draw_graph_axes(bx, by, bw, bh, title, y_max, y_label, min_y=0):
    canvas.create_rectangle(bx, by, bx+bw, by+bh, fill="#111111", outline="white")
    canvas.create_text(bx+5, by+5, anchor="nw", text=title, fill="white", font=("Arial", 9, "bold"))
    canvas.create_text(bx+bw-5, by+bh-5, anchor="se", text="Time (s)", fill="#888888", font=("Arial", 8))
    canvas.create_text(bx+5, by+22, anchor="nw", text=y_label, fill="#888888", font=("Arial", 8))
    
    canvas.create_text(bx-5, by, anchor="e", text=f"{y_max}", fill="white", font=("Arial", 8))
    canvas.create_text(bx-5, by+bh, anchor="e", text=f"{min_y}", fill="white", font=("Arial", 8))
    canvas.create_text(bx, by+bh+5, anchor="n", text="0s", fill="white", font=("Arial", 8))
    canvas.create_text(bx+bw, by+bh+5, anchor="n", text="4s", fill="white", font=("Arial", 8))
    
    if min_y < 0:
        zero_y = by + bh - int(((-min_y) / (y_max - min_y)) * bh)
        canvas.create_line(bx, zero_y, bx+bw, zero_y, fill="#444444", dash=(4,4))

def plot_data(bx, by, bw, bh, x_data, y_data, y_max, color, min_y=0):
    if len(x_data) < 2: return
    max_t = 4.0
    y_range = y_max - min_y
    
    pts = []
    for t, y in zip(x_data, y_data):
        px = bx + int((t / max_t) * bw)
        py = by + bh - int(((y - min_y) / y_range) * bh)
        if bx <= px <= bx+bw and by <= py <= by+bh:
            pts.append((px, py))
            
    for i in range(len(pts)-1):
        canvas.create_line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], fill=color, width=2)

def draw_scene(result_text="", text_color_rgb=(255, 255, 255)):
    canvas.delete("all")
    
    # 배경 및 구조물 그리기
    canvas.create_rectangle(0, HEIGHT-10, 950, HEIGHT, fill="#228B22", outline="") 
    canvas.create_rectangle(target_x, 0, 950, HEIGHT, fill="#c8c8c8", outline="") 
    canvas.create_rectangle(target_x - window_w, target_y - window_h//2, target_x, target_y + window_h//2, fill="#00ffff", outline="") 
    
    if not is_flying:
        rad = math.radians(angle)
        end_x = start_x + int(v0 * math.cos(rad) * 0.8)
        end_y = start_y - int(v0 * math.sin(rad) * 0.8)
        canvas.create_line(start_x, start_y, end_x, end_y, fill="yellow", width=2)
        
    for pt in trail:
        if pt[0] <= 950:
            canvas.create_oval(pt[0]-1, pt[1]-1, pt[0]+1, pt[1]+1, fill="#ff6464", outline="")
        
    r_pixel = max(3, int(r_ball * PPM))
    if ball_x <= 950:
        canvas.create_oval(ball_x - r_pixel, ball_y - r_pixel, ball_x + r_pixel, ball_y + r_pixel, fill="white", outline="black")
    
    graph_x = 1000
    graph_w = 300
    graph_h = 200
    
    dynamic_y_max_h = 150 if v0 > 50 else 25
    dynamic_y_max_v = 160 if v0 > 50 else 45
    
    # 1. 높이 - 시간 (h-t) 그래프
    draw_graph_axes(graph_x, 50, graph_w, graph_h, "1. Height - Time (h-t)", dynamic_y_max_h, "H (m)", min_y=0)
    plot_data(graph_x, 50, graph_w, graph_h, time_data, height_data, dynamic_y_max_h, "#00ffff", min_y=0)
    
    # 2. 속도 - 시간 (v-t) 그래프
    draw_graph_axes(graph_x, 320, graph_w, graph_h, "2. Velocity - Time (v-t)", dynamic_y_max_v, "V (m/s)", min_y=-dynamic_y_max_v)
    plot_data(graph_x, 320, graph_w, graph_h, time_data, vx_data, dynamic_y_max_v, "#ffcc00", min_y=-dynamic_y_max_v)       
    plot_data(graph_x, 320, graph_w, graph_h, time_data, vy_data, dynamic_y_max_v, "#ff4d4d", min_y=-dynamic_y_max_v)       
    plot_data(graph_x, 320, graph_w, graph_h, time_data, v_total_data, dynamic_y_max_v, "white", min_y=-dynamic_y_max_v)    
    
    canvas.create_text(graph_x, 545, anchor="nw", text="-- Vx (Yellow)  -- Vy (Red)  -- V_total (White)", fill="white", font=("Arial", 8))

    ui_text = (
        f"[ CONTROL ]\n"
        f"▶ Up/Down Arrow: Angle ({angle:.1f}deg)\n"
        f"▶ W / S Key: Speed ({v0:.1f} m/s) [Range: 0~150]\n"
        f"▶ SPACE Key: LAUNCH\n"
        f"▶ R Key: RESET\n\n"
        f"[ ENVIRONMENT ]\n"
        f"■ Ball: 145g / Air Resistance ON (Cd=0.3)\n"
        f"■ Window: 5mm Thick Float Glass\n"
        f"■ Target Distance: 57.45m (Height 6.0m)"
    )
    canvas.create_text(20, 20, anchor="nw", text=ui_text, fill="white", font=("Arial", 10))
    if result_text:
        hex_color = '#%02x%02x%02x' % text_color_rgb
        canvas.create_text(20, 240, anchor="nw", text=result_text, fill=hex_color, font=("Arial", 11, "bold"))

# --- 7. 키보드 입력 처리 ---
def key_pressed(event):
    global angle, v0, is_flying, ball_x, ball_y, vx, vy, trail, current_time
    global time_data, height_data, vx_data, vy_data, v_total_data
    key = event.keysym.lower()
    if not is_flying:
        if key == "up": angle = min(angle + 0.5, 90.0)
        elif key == "down": angle = max(angle - 0.5, 0.0)
        elif key == "w": v0 = min(v0 + 0.5, 150.0)
        elif key == "s": v0 = max(v0 - 0.5, 0.0)
        elif key == "space":
            time_data, height_data, vx_data, vy_data, v_total_data = [], [], [], [], []
            current_time = 0.0
            ball_x, ball_y = float(start_x), float(start_y)
            trail = []
            rad = math.radians(angle)
            vx = v0 * math.cos(rad)
            vy = -v0 * math.sin(rad)
            is_flying = True
            update_physics()
    if key == "r":
        is_flying = False
        ball_x, ball_y = float(start_x), float(start_y)
        vx, vy = 0.0, 0.0
        trail = []
        time_data, height_data, vx_data, vy_data, v_total_data = [], [], [], [], []
        current_time = 0.0
        draw_scene()

root.bind("<Key>", key_pressed)
draw_scene()
root.mainloop()
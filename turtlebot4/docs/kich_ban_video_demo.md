# KỊCH BẢN QUAY VIDEO DEMO BÀI THỰC HÀNH 04
## TurtleBot 4 Simulation – SLAM Toolbox, AMCL Localization & Nav2 Navigation (ROS 2 Jazzy & Gazebo Harmonic)

---

### THÔNG TIN TỔNG QUAN VỀ VIDEO
* **Thời lượng mục tiêu:** 7 – 10 phút.
* **Độ phân giải khuyến nghị:** 1080p (1920x1080), 30fps hoặc 60fps.
* **Bố cục màn hình đề xuất:** 
  * Nửa trái màn hình: Môi trường mô phỏng 3D Gazebo Sim (Gazebo Harmonic).
  * Nửa phải màn hình: Giao diện RViz2 (hiển thị Map, LaserScan, TF, Costmap, Path, Goal).
  * Góc dưới: Cửa sổ Terminal hiển thị dòng lệnh và log thực thi.
* **Âm thanh:** Thu âm thuyết minh trực tiếp (hoặc chèn Voice-over) rõ ràng, kèm phụ đề ngắn gọn ở các bước quan trọng.

---

### CHUẨN BỊ TRƯỚC KHI BẤM QUAY (CHECKLIST)
1. **Kiểm tra môi trường:** Đảm bảo ROS 2 Jazzy, Gazebo Harmonic đã cài đặt và build workspace thành công (`colcon build --symlink-install`).
2. **Sắp xếp cửa sổ:** Đặt Gazebo bên trái, RViz2 bên phải, Terminal bên dưới để người chấm theo dõi được tính đồng bộ giữa thực tế mô phỏng và phần mềm xử lý.
3. **Thư mục lưu map:** Tạo sẵn `mkdir -p ~/turtlebot4_maps`.
4. **Kế hoạch 3 Goal Navigation:** Chọn sẵn 3 vị trí đích an toàn trên map (tránh vật cản, đủ rộng để xoay xe).

---

## CHI TIẾT KỊCH BẢN TỪNG PHÂN CẢNH

```
+-----------------------------------------------------------------------------------------+
| PHÂN CẢNH 1: GIỚI THIỆU & KHỞI CHẠY MÔ PHỎNG (Thời lượng: 00:00 – 01:15)                 |
+-----------------------------------------------------------------------------------------+
```
* **Mục tiêu:** Giới thiệu thông tin đề tài, sinh viên, cấu hình môi trường và khởi chạy TurtleBot 4 trong Gazebo Harmonic.
* **Hành động trên màn hình:**
  1. Chiếu slide/tiêu đề mở đầu: Tên bài thực hành, Họ tên sinh viên, MSSV, Lớp, Hệ điều hành Ubuntu 24.04 LTS, ROS 2 Jazzy Jalisco.
  2. Mở Terminal 1 và nhập lệnh khởi chạy Gazebo mô phỏng:
     ```bash
     source /opt/ros/jazzy/setup.bash
     ros2 launch turtlebot4_gz_bringup turtlebot4_gz.launch.py \
       world:=depot model:=standard rviz:=false localization:=false slam:=false nav2:=false
     ```
  3. Màn hình Gazebo Harmonic xuất hiện thế giới mô phỏng `depot` cùng robot TurtleBot 4 Standard tại tọa độ gốc.
  4. Mở Terminal 2 chạy RViz2 để quan sát trực quan:
     ```bash
     source /opt/ros/jazzy/setup.bash
     source ~/turtlebot4/install/setup.bash
     rviz2 -d $(ros2 pkg prefix tb4_simulation_lab)/share/tb4_simulation_lab/config/tb4_simulation_lab.rviz
     ```
* **Lời thuyết minh mẫu (Voice-over):**
  > *"Xin chào thầy cô và các bạn. Hôm nay em xin trình bày bài thực hành số 04: Mô phỏng TurtleBot 4 trên ROS 2 Jazzy và Ubuntu 24.04 LTS. Trước tiên, em khởi chạy thế giới mô phỏng Gazebo Harmonic bằng package turtlebot4_gz_bringup. Robot TurtleBot 4 Standard đã xuất hiện hoàn chỉnh trong không gian mô phỏng cùng hệ thống cảm biến LiDAR RPLiDAR A1 và cụm đế truyền động iRobot Create 3. Đồng thời em mở RViz2 với file cấu hình riêng của đề tài để theo dõi dữ liệu."*

---

```
+-----------------------------------------------------------------------------------------+
| PHÂN CẢNH 2: KIỂM TRA & XÁC MINH CÁC TOPIC CHÍNH (Thời lượng: 01:15 – 02:15)            |
+-----------------------------------------------------------------------------------------+
```
* **Mục tiêu:** Chứng minh các topic quan trọng `/scan`, `/odom`, `/cmd_vel` hoạt động chuẩn xác theo yêu cầu đề bài.
* **Hành động trên màn hình:**
  1. Mở Terminal 3, chạy script kiểm tra tự động đã viết:
     ```bash
     source /opt/ros/jazzy/setup.bash
     source ~/turtlebot4/install/setup.bash
     ros2 run tb4_simulation_lab check_topics.sh
     ```
     *(Terminal hiển thị các dòng màu xanh OK cho /scan, /odom, /cmd_vel kiểu TwistStamped, /tf).*
  2. Thực hiện kiểm tra thủ công bằng lệnh ROS 2 trực tiếp:
     ```bash
     ros2 topic info /scan
     ros2 topic echo /scan --once
     ros2 topic info /odom
     ros2 topic echo /odom --once
     ```
  3. Mở Terminal 4 chạy teleop thử nghiệm vận tốc và quan sát robot di chuyển trong Gazebo:
     ```bash
     ros2 topic info -v /cmd_vel
     ```
     Giữ L1 và đẩy nhẹ cần trái để tiến/lùi, trái/phải để xoay; R1 bật turbo. Nhả L1 để dừng. Cho thấy `/odom` cập nhật và robot chuyển động trong Gazebo.
* **Lời thuyết minh mẫu (Voice-over):**
  > *"Tiếp theo, em kiểm tra các topic cốt lõi bằng script check_topics.sh. Dữ liệu LiDAR /scan và odometry /odom đang phát liên tục. Lệnh vận tốc /cmd_vel dùng TwistStamped. Em dùng joystick TurtleBot 4: giữ L1 để enable, điều khiển cần trái để di chuyển và thấy odometry cùng scan thay đổi trong RViz2."*

---

```
+-----------------------------------------------------------------------------------------+
| PHÂN CẢNH 3: KHẢO SÁT & XÂY DỰNG BẢN ĐỒ VỚI SLAM TOOLBOX (Thời lượng: 02:15 – 04:30)     |
+-----------------------------------------------------------------------------------------+
```
* **Mục tiêu:** Chạy SLAM Toolbox ở chế độ async, điều khiển robot phủ kín bản đồ, thực hiện loop closure và xuất file `map.yaml` + `map.pgm`.
* **Hành động trên màn hình:**
  1. Mở Terminal chạy SLAM Toolbox:
     ```bash
     source /opt/ros/jazzy/setup.bash
     source ~/turtlebot4/install/setup.bash
     ros2 launch tb4_simulation_lab slam.launch.py
     ```
  2. Trên RViz2, lớp `Map` hiện ra dạng Occupancy Grid cập nhật theo thời gian thực (đổi Fixed Frame sang `map`).
  3. Dùng joystick đã được bật cùng Gazebo; giữ L1 rồi điều khiển cần trái ở tốc độ thường để robot di chuyển.
  4. Tua nhanh video (Fast-forward 2x-4x) quá trình robot đi vòng quanh các góc tường, hành lang của khu vực nhà kho.
  5. **Điểm nhấn bắt buộc:** Cho robot đi quay lại điểm xuất phát ban đầu để thực hiện **Loop Closure**. Chỉ con trỏ chuột vào RViz2 thấy các vách tường được căn chỉnh thẳng tắp, không bị lệch hay nhân đôi tường.
  6. Nhả L1 để dừng robot, giữ joystick và node SLAM đang chạy.
  7. Mở terminal mới thực hiện lệnh lưu bản đồ:
     ```bash
     mkdir -p ~/turtlebot4_maps
     ros2 run nav2_map_server map_saver_cli -f ~/turtlebot4_maps/depot_map --ros-args -p use_sim_time:=true -p save_map_timeout:=10.0
     ```
  8. Kiểm tra file map đã tạo thành công:
     ```bash
     ls -lh ~/turtlebot4_maps/depot_map.yaml ~/turtlebot4_maps/depot_map.pgm
     cat ~/turtlebot4_maps/depot_map.yaml
     ```
* **Lời thuyết minh mẫu (Voice-over):**
  > *"Bây giờ em tiến hành lập bản đồ môi trường bằng SLAM Toolbox. Thuật toán sử dụng cơ chế Graph-Based SLAM với Ceres Solver để tối ưu hóa đồ thị tư thế robot. Em điều khiển robot di chuyển với vận tốc vừa phải 0.2 m/s để LiDAR thu thập đủ số lượng tia phản xạ. Khi robot quay trở lại vị trí cũ, thuật toán phát hiện đóng vòng Loop Closure và nắn chỉnh toàn bộ đồ thị, triệt tiêu hoàn toàn sai số trôi dạt của odometry. Bản đồ hiển thị trên RViz2 rất sắc nét, vách tường rõ ràng. Em dùng công cụ map_saver_cli để lưu thành công hai file depot_map.yaml và depot_map.pgm."*

---

```
+-----------------------------------------------------------------------------------------+
| PHÂN CẢNH 4: KHỞI ĐỘNG LOCALIZATION VÀ ƯỚC LƯỢNG VỊ TRÍ BAN ĐẦU (Thời lượng: 04:30 – 05:45) |
+-----------------------------------------------------------------------------------------+
```
* **Mục tiêu:** Tắt node SLAM, tải bản đồ tĩnh đã lưu, chạy AMCL và ước lượng vị trí bằng "2D Pose Estimate".
* **Hành động trên màn hình:**
  1. Tắt terminal SLAM bằng `Ctrl+C` (nhấn mạnh nguyên tắc không chạy SLAM và AMCL đồng thời).
  2. Giữ nguyên Gazebo (hoặc reset vị trí robot).
  3. Khởi chạy stack Localization:
     ```bash
     source /opt/ros/jazzy/setup.bash
     source ~/turtlebot4/install/setup.bash
     ros2 launch tb4_simulation_lab localization.launch.py map:=/home/$USER/turtlebot4_maps/depot_map.yaml
     ```
  4. Trên RViz2, bản đồ tĩnh `depot_map` xuất hiện. Các tia LiDAR đỏ ban đầu có thể chưa trùng khít với tường đen.
  5. Chọn công cụ **2D Pose Estimate** trên thanh công cụ RViz:
     * Nhấp chuột vào vị trí robot tương ứng trong Gazebo, kéo chuột theo hướng mũi tên trùng với hướng đầu xe của robot (yaw).
  6. Quan sát Particle Cloud (tập hợp các mũi tên xanh biểu diễn hạt của bộ lọc Monte Carlo) tập trung dày đặc lại xung quanh robot, và tia LiDAR màu đỏ khớp 100% lên các vách tường màu đen trên bản đồ.
  7. Kiểm tra topic vị trí ước lượng:
     ```bash
     ros2 topic echo /amcl_pose --once
     ```
* **Lời thuyết minh mẫu (Voice-over):**
  > *"Sau khi có bản đồ tĩnh, em dừng node SLAM và khởi chạy stack Localization sử dụng AMCL (Adaptive Monte Carlo Localization) kết hợp map_server. Em sử dụng công cụ 2D Pose Estimate trên RViz2 để cung cấp vị trí khởi tạo x, y và góc quay theta ban đầu. Ngay lập tức, bộ lọc hạt (Particle Filter) tính toán trọng số cảm biến Likelihood Field và hội tụ nhanh chóng. Như thầy cô thấy, các điểm quét laser màu đỏ đã khớp hoàn hảo với các vách tường trên bản đồ tĩnh, transform map to odom được công bố chính xác."*

---

```
+-----------------------------------------------------------------------------------------+
| PHÂN CẢNH 5: NAVIGATION VỚI NAV2 – THỰC HIỆN 03 GOALS TỰ ĐỘNG (Thời lượng: 05:45 – 08:30) |
+-----------------------------------------------------------------------------------------+
```
* **Mục tiêu:** Khởi chạy Nav2 stack, lập đường đi tự động và di chuyển thành công tới 3 vị trí đích khác nhau mà không hề can thiệp teleop.
* **Hành động trên màn hình:**
  1. Giữ nguyên Gazebo và Localization đang chạy. Mở terminal mới khởi chạy Navigation:
     ```bash
     source /opt/ros/jazzy/setup.bash
     source ~/turtlebot4/install/setup.bash
     ros2 launch tb4_simulation_lab navigation.launch.py
     ```
  2. Quan sát trên RViz2: Global Costmap và Local Costmap hiện lên với các dải Inflation bao quanh vật cản.

  3. **Thực hiện GOAL 1 (Khu vực hành lang bên phải):**
     * Chọn công cụ **Nav2 Goal** trên thanh công cụ RViz2.
     * Nhấp và kéo chuột tại vị trí đích số 1.
     * Quay cận cảnh: Đường Global Path (vạch xanh) xuất hiện do NavFn Planner tính toán. Local Trajectory do DWB Controller tạo ra.
     * Robot trong Gazebo tự động lăn bánh bám theo quỹ đạo, tự giảm tốc khi vào cua và dừng chính xác tại đích 1.
     * Terminal hiển thị log Goal reached / Succeeded.

  4. **Thực hiện GOAL 2 (Khu vực kệ hàng đối diện):**
     * Chọn lại **Nav2 Goal**, nhấp vào vị trí đích số 2 ở một khu vực xa hơn có chướng ngại vật trung gian.
     * Quan sát xe tự động tránh vật cản trung gian nhờ Costmap Inflation Layer và DWB Controller né chướng ngại vật linh hoạt.
     * Robot đến đích 2 và xoay đúng góc yaw mong muốn.

  5. **Thực hiện GOAL 3 (Quay về gần điểm xuất phát ban đầu):**
     * Chọn **Nav2 Goal** đưa robot quay về vị trí ban đầu.
     * Robot tự quay đầu, di chuyển dứt khoát và hoàn thành goal số 3 an toàn 100%, không xảy ra va chạm.
     * *(Hoặc trình diễn chạy tự động bằng script `ros2 run tb4_simulation_lab send_nav_goals.py` để thể hiện tính tự động hoá cao cấp).*
* **Lời thuyết minh mẫu (Voice-over):**
  > *"Tiếp theo là phần trọng tâm: Tự hành với Nav2 stack. Khi em đặt Goal 1 bằng công cụ Nav2 Goal, Global Planner NavFn sử dụng thuật toán A* để tính đường đi tối ưu toàn cục. DWB Local Controller liên tục rollout các quỹ đạo vận tốc khả thi, đánh giá bằng hàm mục tiêu để điều khiển robot né vật cản an toàn. Robot đã đến Goal 1 thành công. Tiếp tục với Goal 2 ở một nhánh hành lang hẹp, robot tự động giảm tốc và lách qua khoảng trống an toàn. Cuối cùng ở Goal 3 quay trở lại điểm xuất phát, robot hoàn thành mượt mà mà không có bất kỳ sự can thiệp thủ công nào bằng bàn phím."*

---

```
+-----------------------------------------------------------------------------------------+
| PHÂN CẢNH 6: TỔNG KẾT & KẾT THÚC (Thời lượng: 08:30 – 09:15)                              |
+-----------------------------------------------------------------------------------------+
```
* **Mục tiêu:** Tóm lược kết quả đạt được, chiếu cấu trúc mã nguồn trên GitHub và kết thúc video.
* **Hành động trên màn hình:**
  1. Hiển thị bảng tổng kết kết quả 3 Goal (Goal 1: Thành công, Goal 2: Thành công, Goal 3: Thành công).
  2. Mở trình duyệt web hiển thị trang GitHub Repository của bài thực hành với đầy đủ mã nguồn, cấu hình và file README.md.
  3. Slide kết thúc: Lời cảm ơn, thông tin liên hệ.
* **Lời thuyết minh mẫu (Voice-over):**
  > *"Như vậy, em đã hoàn thành toàn bộ yêu cầu của Bài thực hành 04: từ mô phỏng TurtleBot 4 trong Gazebo Harmonic, kiểm tra topic cảm biến, tạo bản đồ với SLAM Toolbox, định vị AMCL và dẫn đường tự động 3 mục tiêu liên tiếp với Nav2. Toàn bộ mã nguồn, file cấu hình và báo cáo chi tiết đã được đăng tải đầy đủ trên GitHub repository. Em xin chân thành cảm ơn thầy cô đã theo dõi!"*

---

### MẸO QUAY VIDEO ĐẠT ĐIỂM TỐI ĐA
* **Không cắt ghép giả tạo:** Không tua nhảy cóc ở phần robot di chuyển đến goal khiến giám thị nghi ngờ việc robot bị teleport hoặc dùng teleop.
* **Giữ con trỏ chuột rời xa bàn phím khi Nav2 đang chạy:** Thể hiện rõ ràng bàn tay/con trỏ chuột không can thiệp điều khiển.
* **Hiển thị song song Gazebo và RViz2:** Đây là bằng chứng quan trọng nhất khẳng định robot ảo trong Gazebo thực sự di chuyển đồng bộ với tính toán trên RViz2.

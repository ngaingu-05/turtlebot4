# BÀI THỰC HÀNH 04 – MÔ PHỎNG TURTLEBOT 4 CƠ BẢN
## SLAM Toolbox, AMCL Localization & Nav2 Navigation trên ROS 2 Jazzy & Gazebo Harmonic

[![ROS 2](https://img.shields.io/badge/ROS%202-Jazzy%20Jalisco-blue.svg)](https://docs.ros.org/en/jazzy/)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-24.04%20LTS-orange.svg)](https://releases.ubuntu.com/24.04/)
[![Gazebo](https://img.shields.io/badge/Gazebo-Harmonic-purple.svg)](https://gazebosim.org/home)
[![TurtleBot 4](https://img.shields.io/badge/Robot-TurtleBot%204%20Standard-green.svg)](https://clearpathrobotics.com/turtlebot-4/)

Workspace này cung cấp mã nguồn, file cấu hình, launch file và tài liệu hướng dẫn hoàn chỉnh để thực hiện **Bài thực hành 04 – TurtleBot 4 Simulation cơ bản**, bao gồm khởi chạy mô phỏng, kiểm tra sensor/actuator, tạo bản đồ với SLAM Toolbox, định vị AMCL và điều hướng tự hành Nav2.

---

## 📌 THÔNG TIN NỘP BÀI (SUBMISSION LINKS)

* **GitHub Repository:** `[Dán link GitHub Repository của bạn tại đây - VD: https://github.com/username/turtlebot4-lab04]`
* **Video Demo (Google Drive):** `[Dán link Google Drive chia sẻ công khai video demo tại đây]`
* **Kịch bản quay video demo:** Xem tại [docs/kich_ban_video_demo.md](docs/kich_ban_video_demo.md)

---

## 📂 CẤU TRÚC THƯ MỤC REPOSITORY

```text
turtlebot4/
├── README.md                                # Hướng dẫn cài đặt và vận hành toàn diện
├── docs/
│   └── kich_ban_video_demo.md               # Kịch bản từng giây kèm lời thoại quay video demo
└── src/
    └── tb4_simulation_lab/
        ├── CMakeLists.txt                   # Quy tắc build và cài đặt thư mục/script ROS 2
        ├── package.xml                      # Khai báo metadata và các package phụ thuộc
        ├── config/
        │   ├── nav2_params.yaml             # Cấu hình chi tiết Nav2 stack (AMCL, DWB, Costmaps, BT)
        │   ├── slam_toolbox_params.yaml     # Cấu hình SLAM Toolbox (Graph-based, Ceres, Loop Closure)
        │   └── tb4_simulation_lab.rviz      # Cấu hình RViz2 trực quan (Map, Scan, TF, AMCL, Costmaps)
        ├── launch/
        │   ├── gazebo_rviz.launch.py        # Launch tiện ích: Khởi chạy Gazebo Sim + RViz2 cùng lúc
        │   ├── slam.launch.py               # Launch SLAM Toolbox chế độ Async Mapping
        │   ├── localization.launch.py       # Launch Nav2 AMCL + Map Server với map tĩnh
        │   └── navigation.launch.py         # Launch Nav2 Stack (Planner, Controller, Behaviors)
        ├── maps/
        │   ├── map.yaml                     # File metadata bản đồ Depot (resolution, origin)
        │   └── map.pgm                      # Ảnh Occupancy Grid Depot đã khảo sát
        └── scripts/
            ├── check_topics.sh              # Script Bash kiểm tra tự động /scan, /odom, /cmd_vel, /tf
            └── send_nav_goals.py            # Node Python gửi goals qua tham số goals_json
```

---

## 🛠️ 1. YÊU CẦU MÔI TRƯỜNG & HƯỚNG DẪN CÀI ĐẶT

### 1.1 Yêu cầu hệ thống
* **Hệ điều hành:** Ubuntu 24.04 LTS (Noble Numbat) native hoặc WSL2 có hỗ trợ GUI (WSLg).
* **ROS 2 Version:** ROS 2 Jazzy Jalisco Desktop.
* **Gazebo Version:** Gazebo Harmonic (`gz-harmonic`) – phiên bản tương thích chính thức với ROS 2 Jazzy.

### 1.2 Cài đặt ROS 2 Jazzy Desktop (nếu máy chưa có)
```bash
sudo apt update && sudo apt install -y locales software-properties-common curl
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
sudo add-apt-repository -y universe

sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

sudo apt update && sudo apt install -y ros-jazzy-desktop ros-dev-tools python3-rosdep python3-colcon-common-extensions
```

### 1.3 Cài đặt Gazebo Harmonic & các Package TurtleBot 4, Nav2, SLAM
```bash
# Cài đặt Gazebo Harmonic
sudo curl -sSL https://packages.osrfoundation.org/gazebo.gpg \
  -o /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] https://packages.osrfoundation.org/gazebo/ubuntu-stable $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
  | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null

sudo apt update
sudo apt install -y gz-harmonic \
  ros-jazzy-turtlebot4-simulator \
  ros-jazzy-irobot-create-nodes \
  ros-jazzy-navigation2 \
  ros-jazzy-nav2-bringup \
  ros-jazzy-slam-toolbox \
  ros-jazzy-turtlebot4-bringup \
  ros-jazzy-joy-linux \
  ros-jazzy-teleop-twist-joy \
  ros-jazzy-teleop-twist-keyboard \
  ros-jazzy-rviz2
```

### 1.4 Biên dịch Workspace
```bash
cd ~/turtlebot4
source /opt/ros/jazzy/setup.bash

# Khởi tạo rosdep nếu chưa chạy lần nào
# sudo rosdep init
rosdep update
rosdep install --from-paths src --ignore-src -r -y

# Build gói lab
colcon build --symlink-install
source install/setup.bash
```

---

## 🚀 2. QUY TRÌNH THỰC HIỆN BÀI THỰC HÀNH TỪNG BƯỚC

### 📍 PHẦN 1: KHỞI CHẠY MÔ PHỎNG & KIỂM TRA TOPIC

#### Bước 1.1: Khởi chạy TurtleBot 4 trong Gazebo Sim
Mở **Terminal 1**:
```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot4/install/setup.bash
ros2 launch tb4_simulation_lab gazebo_rviz.launch.py \
  world:=depot model:=standard joy:=false
```
Lệnh này khởi chạy Gazebo Harmonic, spawn robot, bridge cảm biến và RViz2. Điều khiển joystick tách riêng để có thể dừng hẳn teleop trước khi chạy Nav2. Mặc định toàn bộ bài thực hành dùng world `depot`.

#### Bước 1.2: RViz2 trực quan
Launch ở Bước 1.1 đã mở RViz2. Nếu chỉ muốn mở lại RViz2 riêng (không chạy thêm Gazebo):
```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot4/install/setup.bash
rviz2 -d "$(ros2 pkg prefix tb4_simulation_lab)/share/tb4_simulation_lab/config/tb4_simulation_lab.rviz"
```

#### Bước 1.3: Chạy script kiểm tra topic tự động
Mở **Terminal 3**:
```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot4/install/setup.bash
ros2 run tb4_simulation_lab check_topics.sh
```
Script sẽ kiểm tra và xác nhận:
* `/scan`: kiểu `sensor_msgs/msg/LaserScan`, có publisher và dữ liệu nhận được.
* `/odom`: kiểu `nav_msgs/msg/Odometry`, có publisher và dữ liệu nhận được.
* `/cmd_vel`: kiểu `geometry_msgs/msg/TwistStamped` (chuẩn trên ROS 2 Jazzy).

#### Bước 1.4: Kiểm tra joystick và điều khiển vận tốc
Kết nối tay cầm và kiểm tra thiết bị/quyền truy cập:
```bash
ls -l /dev/input/js0
```
Mở Terminal 4 để chạy điều khiển stock:
```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot4/install/setup.bash
ros2 launch turtlebot4_bringup joy_teleop.launch.py namespace:=/ joy_device:=/dev/input/js0
```
Không có joystick thì không chạy launch trên; dùng bàn phím dự phòng ở dưới.
Launch joystick và `turtlebot4_controller.config.yaml` được dùng trực tiếp từ `turtlebot4_bringup`, không sao chép vào package lab. Khi launch riêng, cần truyền `namespace:=/`.

| Điều khiển | Tác dụng |
|---|---|
| Giữ L1 (shoulder trái) | Cho phép điều khiển thường |
| Cần trái lên/xuống | Tiến/lùi |
| Cần trái trái/phải | Xoay |
| Giữ R1 (shoulder phải) cùng cần trái | Chế độ tốc độ turbo |

Nhả nút enable để dừng phát lệnh chuyển động. Dừng teleop bằng `Ctrl+C` sau khi kiểm tra. Khi không có joystick, dùng bàn phím dự phòng:
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true -p use_sim_time:=true -p speed:=0.15 -p turn:=0.5
```
Không chạy bàn phím cùng lúc với joystick hoặc Nav2 vì tất cả cùng có thể phát lệnh vận tốc.

---

### 📍 PHẦN 2: XÂY DỰNG BẢN ĐỒ BẰNG SLAM TOOLBOX

Giữ nguyên terminal Gazebo/RViz2 trong quá trình mapping. Joystick teleop chỉ chạy trong thời gian khảo sát; phải dừng node teleop hoàn toàn trước khi bật Nav2.

#### Bước 2.1: Khởi chạy SLAM Toolbox (Async Mapping)
Mở **Terminal 3**:
```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot4/install/setup.bash
ros2 launch tb4_simulation_lab slam.launch.py
```
Trên RViz2, đổi **Global Options → Fixed Frame** từ `odom` sang `map`. Bản đồ Occupancy Grid sẽ được cập nhật trong quá trình khảo sát.

#### Bước 2.2: Điều khiển robot khảo sát môi trường bằng joystick
Trong một terminal riêng, chạy driver và teleop joystick:
```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot4/install/setup.bash
ros2 launch turtlebot4_bringup joy_teleop.launch.py namespace:=/ joy_device:=/dev/input/js0
```
* Giữ L1, đẩy nhẹ cần trái để di chuyển chậm qua các hành lang và vật cản; phối hợp trái/phải để rẽ.
* Dùng R1 turbo chỉ khi cần di chuyển nhanh ở khoảng trống. Mapping nên ưu tiên tốc độ thường để scan ổn định.
* **Lưu ý tạo Loop Closure:** Cho robot quay lại khu vực xuất phát ban đầu để SLAM Toolbox đóng vòng lặp và tối ưu đồ thị (Pose Graph), triệt tiêu hiện tượng lệch vách tường.
* Mặc định thiết bị là `/dev/input/js0`, có thể đổi bằng `joy_device:=/dev/input/js1`.

#### Bước 2.3: Xuất và lưu bản đồ
Sau khi phủ kín bản đồ, dừng joystick teleop bằng `Ctrl+C`, giữ Gazebo và node SLAM. Mở terminal mới gõ lệnh lưu:
```bash
source /opt/ros/jazzy/setup.bash
mkdir -p ~/turtlebot4_maps
ros2 run nav2_map_server map_saver_cli -f ~/turtlebot4_maps/depot_map --ros-args -p use_sim_time:=true -p save_map_timeout:=10.0
```
Kiểm tra kết quả:
```bash
ls -lh ~/turtlebot4_maps/depot_map.yaml ~/turtlebot4_maps/depot_map.pgm
```
Sau khi lưu xong, dừng node SLAM ở Terminal 3 (`Ctrl+C`), dừng Gazebo rồi khởi động lại cùng world `depot` trước khi chạy localization.

---

### 📍 PHẦN 3: LOCALIZATION (ĐỊNH VỊ VỚI AMCL)

*Chú ý: Không chạy SLAM và AMCL cùng lúc để tránh xung đột transform `map -> odom`.*

#### Bước 3.1: Khởi chạy AMCL với bản đồ vừa lưu
Mở **Terminal 3**:
```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot4/install/setup.bash
ros2 launch tb4_simulation_lab localization.launch.py map:=/home/$USER/turtlebot4_maps/depot_map.yaml
```

#### Bước 3.2: Ước lượng vị trí ban đầu (2D Pose Estimate)
1. Quan sát vị trí và hướng thực tế của robot trong cửa sổ Gazebo.
2. Trên thanh công cụ RViz2, chọn công cụ **2D Pose Estimate**.
3. Nhấp chuột vào vị trí tương ứng trên bản đồ và kéo một mũi tên theo đúng hướng đầu robot (yaw).
4. Quan sát: Các tia laser đỏ (`/scan`) sẽ khớp hoàn toàn vào các vách tường màu đen trên bản đồ, và đám mây hạt (Particle Cloud) hội tụ quanh thân xe.
5. Kiểm tra vị trí ước lượng:
   ```bash
   ros2 topic echo /amcl_pose --once
   ```

---

### 📍 PHẦN 4: NAVIGATION VỚI NAV2 (THỰC HIỆN 03 GOALS)

Giữ nguyên **Gazebo** và **Localization** đang chạy.

#### Bước 4.1: Khởi chạy Nav2 Stack
Mở **Terminal 4**:
```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot4/install/setup.bash
ros2 launch tb4_simulation_lab navigation.launch.py
```
*(Trên RViz2, các lớp Costmap toàn cục và cục bộ với dải Inflation bao quanh vật cản sẽ xuất hiện).*

#### Bước 4.2: Điều hướng tự động (2 lựa chọn)

##### Cách 1: Đặt đích thủ công bằng công cụ RViz2 (Khuyến nghị cho video)
1. Chọn công cụ **Nav2 Goal** trên thanh công cụ RViz2.
2. Nhấp và kéo chuột tại **Điểm đích 1** (khu vực trống, an toàn).
   * Quan sát đường dẫn màu xanh (Global Path) xuất hiện.
   * Robot trong Gazebo tự động lăn bánh di chuyển mượt mà tới đích mà **không dùng teleop**.
3. Sau khi robot dừng hẳn và báo thành công, tiếp tục đặt **Điểm đích 2** ở một góc hành lang khác.
4. Sau khi hoàn thành Goal 2, đặt **Điểm đích 3** quay về gần điểm xuất phát ban đầu.

##### Cách 2: Tự động chạy tuần tự 3 Goals bằng Node Python
Mở **Terminal 5**:
```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot4/install/setup.bash
ros2 run tb4_simulation_lab send_nav_goals.py
```
Script cần tham số `goals_json` dạng `[[x, y, yaw_độ], ...]`, lấy từ các vị trí trống trên bản đồ depot thực tế. Không có goals thì script dừng; không dùng lại tọa độ warehouse. Ưu tiên đặt goals bằng RViz theo yêu cầu bài.

---

## 📚 3. TÀI LIỆU THAM KHẢO

* [Hướng dẫn mô phỏng TurtleBot 4 chính thức](https://turtlebot.github.io/turtlebot4-user-manual/software/turtlebot4_simulator.html)
* [Tài liệu ROS 2 Jazzy Jalisco](https://docs.ros.org/en/jazzy/)
* [SLAM Toolbox Documentation](https://github.com/SteveMacenski/slam_toolbox)
* [Nav2 - Navigation 2 Stack](https://docs.nav2.org/)

## Tái sử dụng package gốc

`gazebo_rviz.launch.py` ghép `ros_gz_sim/gz_sim.launch.py` và `turtlebot4_gz_bringup/turtlebot4_spawn.launch.py` gốc với RViz của lab, chọn renderer Ogre2. LiDAR, bridge, odometry, mô hình và controller đều do các package gốc cung cấp. Bài mô phỏng dùng các package ROS đã cài, không cần clone hoặc build driver phần cứng.

Để chạy simulator độc lập với package lab:

```bash
source /opt/ros/jazzy/setup.bash
ros2 launch turtlebot4_gz_bringup turtlebot4_gz.launch.py world:=depot model:=standard rviz:=true
```

Robot khởi tạo trên dock. Trước khi teleop, thực hiện undock và chờ action kết thúc:

```bash
ros2 action send_goal /undock irobot_create_msgs/action/Undock '{}'
```

Nếu `/wheel_status` báo `wheels_enabled: false`, kiểm tra nút E-stop trong Gazebo. Sau khi xác nhận có thể tiếp tục chuyển động trong mô phỏng:

```bash
ros2 service call /e_stop irobot_create_msgs/srv/EStop '{e_stop_on: false}'
```

Trong RViz, dùng Fixed Frame `odom` khi chưa chạy SLAM/AMCL; chuyển sang `map` sau khi hệ thống phát transform `map -> odom`.

## World depot trên máy hiện tại

Mặc định launch dùng `depot`; SLAM → lưu `~/turtlebot4_maps/depot_map.yaml` + `.pgm` → AMCL → Nav2 dùng cùng bản đồ này. Bản đồ trong package đã được thay bằng kết quả khảo sát Depot. Phải khảo sát depot và lưu map mới trước khi chạy AMCL/Nav2.

Launch lab giữ spawn, bridge LiDAR và controller gốc; chỉ ép renderer server `ogre2` vì Ogre1 trả mọi tia về range_min trên máy này. RViz dùng software rendering. Log shader có thể vẫn xuất hiện; đã kiểm tra trực tiếp map và scan hiển thị được.

Nếu Gazebo đứng ở bước tải Depot, tải model trước:

```bash
gz fuel download -u https://fuel.gazebosim.org/1.0/OpenRobotics/models/Depot
```

Máy hiện tại đã có Depot v6 trong cache `fuel.ignitionrobotics.org`; đã sao chép sang cache `fuel.gazebosim.org` để không cần tải lại. Không chỉnh package hệ thống.

## Chuẩn bị repository GitHub

Chỉ đưa mã nguồn lab, README và tài liệu/minh chứng vào repository. `.gitignore` loại build/install/log, cache Python và cấu hình IDE. Caveman và repository clone tham khảo đã được xóa khỏi workspace.

Repo upstream: https://github.com/turtlebot/turtlebot4_robot (nhánh Jazzy; commit tham khảo `28e115f`). Bài mô phỏng dùng package đã cài qua apt, không cần clone này để build package lab.

Sau khi clone repository của bài, tạo lại build/install bằng:

```bash
source /opt/ros/jazzy/setup.bash
colcon build --packages-select tb4_simulation_lab --symlink-install
source install/setup.bash
```

Bản đồ trong package là kết quả khảo sát Depot. Để dùng trực tiếp bản đồ trong repository khi không có `~/turtlebot4_maps`, chạy:

```bash
ros2 launch tb4_simulation_lab localization.launch.py \
  map:="$(ros2 pkg prefix tb4_simulation_lab)/share/tb4_simulation_lab/maps/map.yaml"
```

Trước khi push, kiểm tra danh sách file bằng `git status --short`; điền thông tin sinh viên và link nộp bài trong tài liệu.

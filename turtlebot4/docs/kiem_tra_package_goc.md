# Kiểm tra tái sử dụng package gốc

Kiểm tra ngày 13/10/2026 trên máy hiện tại.

- Repo clone: `turtlebot/turtlebot4_robot`, nhánh Jazzy, commit `28e115f`. Đây là các package robot thật; `rplidar.launch.py` mở cổng `/dev/RPLIDAR`, không dùng cho LiDAR mô phỏng.
- Simulator thực tế nằm trong `turtlebot4_gz_bringup` và các package iRobot đã cài tại `/opt/ros/jazzy`.
- Chạy trực tiếp simulator gốc, không source workspace lab, với `world:=maze model:=standard`: nhận được `/scan` (frame `turtlebot4/rplidar_link/rplidar`), `/odom`; controller nhận `TwistStamped`.
- Sau undock và tắt E-stop trong mô phỏng, gửi lệnh 0,1 m/s rồi lệnh dừng: odometry thay đổi khoảng 0,1625 m. Thử nghiệm giới hạn này xác nhận đường điều khiển hoạt động; không phải bằng chứng hoàn thành navigation.
- Launch lab rút gọn build thành công, gọi simulator gốc và mở RViz; nhận được `/scan`, không cần bridge LiDAR riêng.
- Joystick dùng launch/config gốc `turtlebot4_bringup`; thử bằng message `/joy` giả lập vì máy không có `/dev/input/js0`. L1 + cần tiến phát 0,2 m/s; nhả L1 phát lệnh dừng 0. Không khẳng định đã thử tay cầm vật lý.
- Để kiểm tra joystick trong khi chờ cài hệ thống, các gói binary chính thức được tải và giải nén tại `/tmp/tb4_stock_deps`, không sửa `/opt/ros`. Cần cài `ros-jazzy-turtlebot4-bringup` và `ros-jazzy-joy-linux` để dùng bình thường sau đó.

Đã bỏ launch Gazebo và joystick tự viết, config joystick sao chép, script pipeline cũ. Giữ launch SLAM/AMCL/Nav2, cấu hình lab, RViz, script kiểm tra topic, script goals và tài liệu. Repo clone được giữ để tham khảo, có `COLCON_IGNORE`; package lab không trỏ vào đường dẫn repo clone.

Bản sao trước khi dọn: `/home/nghia/tb4_cleanup_backup/before-stock-reuse.tar.gz`.

## Cập nhật depot

Kiểm tra sâu hơn: Ogre1 có message `/scan` nhưng tất cả 640 tia bằng 0,164 m, không đủ dùng SLAM. Launch hiện tại gọi `ros_gz_sim` với `--render-engine-server ogre2` và spawn/bridge/controller gốc. Với depot, nhận scan 1,48–11,94 m, có odometry, SLAM tạo map ban đầu 414×301 ô ở resolution 0,05 m. Đây là kiểm tra khởi động, chưa phải bản đồ khảo sát đầy đủ.

Gazebo bị kẹt tải Depot qua Fuel; đã tái sử dụng cache Depot v6 có sẵn. Mặc định localization chuyển sang `~/turtlebot4_maps/depot_map.yaml`. Goals cũ cho warehouse đã bỏ; script nhận `goals_json` từ bản đồ thực tế.

Depot sau sửa cache: Gazebo và RViz hiển thị được; scan 640 tia có khoảng cách khác nhau, có odometry, map 414×301. Lưu thử YAML/PGM tại `/tmp/tb4_depot_smoke_map.*` thành công. RViz vẫn có log shader nhưng ảnh kiểm tra cho thấy map/scan được vẽ. Phiên thử dùng `ROS_DOMAIN_ID=74`.

## Sau khảo sát và localization

Đã lưu `~/turtlebot4_maps/depot_map.yaml` và `.pgm`: 604×304 ô, resolution 0,05 m; khoảng 170.897 ô trống, 5.776 ô vật cản. Quan sát ảnh map: có tường bao, vật cản chính; chưa thấy nhân đôi tường rõ rệt. Đã chép kết quả vào `src/tb4_simulation_lab/maps/map.yaml` và `map.pgm`.

Dừng SLAM, khởi động lại Depot, chạy AMCL. Bỏ `map_server.yaml_filename` rỗng trong tham số dùng chung vì nó ghi đè đường dẫn map do launch truyền vào. Map server nạp đúng 604×304; đặt initial pose tại vị trí spawn (0,0,0), nhận pose AMCL x≈−0,001 m, y≈−0,064 m, yaw≈0,003 rad. Chưa thực hiện navigation goals.

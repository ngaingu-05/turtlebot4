#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =============================================================================
# File: send_nav_goals.py
# Mô tả: Node ROS 2 gửi 3 mục tiêu điều hướng (navigation goals) tuần tự
#         đến Nav2 sử dụng action NavigateToPose.
#
# Node này sẽ:
#   1. Kết nối đến Nav2 action server (navigate_to_pose)
#   2. Gửi lần lượt 3 mục tiêu (goals) đến robot
#   3. Chờ mỗi mục tiêu hoàn thành trước khi gửi mục tiêu tiếp theo
#   4. In trạng thái (chấp nhận, từ chối, thành công, thất bại) bằng tiếng Việt
#
# Sử dụng:
#   ros2 run tb4_simulation_lab send_nav_goals.py
#
# Hoặc chạy trực tiếp:
#   python3 send_nav_goals.py
# =============================================================================

# --- Import các thư viện cần thiết ---

import rclpy                              # Thư viện Python chính cho ROS 2
from rclpy.node import Node               # Lớp cơ sở để tạo ROS 2 node
from rclpy.action import ActionClient      # Client để gọi action server
from rclpy.parameter import Parameter      # Để khai báo tham số ROS 2

# Import kiểu tin nhắn PoseStamped - dùng để mô tả vị trí và hướng mục tiêu
from geometry_msgs.msg import PoseStamped

# Import action NavigateToPose - action chính của Nav2 để điều hướng robot
from nav2_msgs.action import NavigateToPose

# Import trạng thái của goal trong action
from action_msgs.msg import GoalStatus

# Import thư viện toán học để chuyển đổi góc Euler sang quaternion
import json
import math
import time


def euler_to_quaternion(yaw):
    """
    Chuyển đổi góc yaw (radian) sang quaternion.

    Trong điều hướng 2D, chúng ta chỉ cần góc yaw (xoay quanh trục Z).
    Roll và pitch được đặt bằng 0.

    Tham số:
        yaw (float): Góc yaw tính bằng radian

    Trả về:
        tuple: (x, y, z, w) - các thành phần quaternion
    """
    # Công thức chuyển đổi Euler -> Quaternion (chỉ có yaw)
    # roll = 0, pitch = 0, chỉ tính yaw
    half_yaw = yaw / 2.0
    qx = 0.0
    qy = 0.0
    qz = math.sin(half_yaw)
    qw = math.cos(half_yaw)
    return (qx, qy, qz, qw)


class SendNavGoals(Node):
    """
    Node ROS 2 gửi các mục tiêu điều hướng tuần tự đến Nav2.

    Node này tạo một action client kết nối đến action server
    'navigate_to_pose' của Nav2, sau đó gửi lần lượt từng mục tiêu
    và chờ kết quả trước khi gửi mục tiêu tiếp theo.
    """

    def __init__(self):
        """
        Khởi tạo node SendNavGoals.

        - Tạo node với tên 'send_nav_goals'
        - Thiết lập use_sim_time = True (bắt buộc khi chạy trong mô phỏng)
        - Tạo action client cho NavigateToPose
        - Nhận mục tiêu do người dùng chọn trên bản đồ depot
        """
        super().__init__('send_nav_goals')

        # --- Thiết lập use_sim_time ---
        # Khi chạy trong Gazebo, phải dùng thời gian mô phỏng thay vì
        # thời gian thực của hệ thống
        self.set_parameters([
            Parameter('use_sim_time', Parameter.Type.BOOL, True)
        ])
        self.get_logger().info('⏱️  Đã bật use_sim_time = True (thời gian mô phỏng)')

        # --- Tạo Action Client ---
        # Action client kết nối đến action server 'navigate_to_pose' của Nav2
        # Action server này do nav2_bt_navigator cung cấp
        self._action_client = ActionClient(
            self,                    # Node hiện tại
            NavigateToPose,          # Kiểu action
            'navigate_to_pose'       # Tên action server
        )
        self.get_logger().info('🔗 Đã tạo Action Client cho navigate_to_pose')

        # JSON list of [x, y, yaw_degrees], chosen on the surveyed depot map.
        # No warehouse coordinates are reused when switching worlds.
        self.declare_parameter('goals_json', '[]')
        coordinates = json.loads(self.get_parameter('goals_json').value)
        if not isinstance(coordinates, list) or any(
            not isinstance(goal, list) or len(goal) != 3
            or any(isinstance(v, bool) or not isinstance(v, (int, float))
                   or not math.isfinite(v) for v in goal)
            for goal in coordinates
        ):
            raise ValueError('goals_json must be a list of finite [x, y, yaw_degrees]')
        self.goals = [
            {'x': float(x), 'y': float(y), 'yaw_deg': float(yaw), 'ten': f'Goal {i + 1}'}
            for i, (x, y, yaw) in enumerate(coordinates)
        ]

        # Biến theo dõi mục tiêu hiện tại
        self._current_goal_index = 0

        # Biến lưu trạng thái hoàn thành
        self._all_goals_done = False

    def send_goals(self):
        """
        Bắt đầu quá trình gửi mục tiêu điều hướng.

        Phương thức này sẽ:
        1. Chờ action server sẵn sàng
        2. Gửi mục tiêu đầu tiên
        (Các mục tiêu tiếp theo được gửi tự động sau khi mục tiêu trước hoàn thành)
        """

        if not self.goals:
            self.get_logger().error(
                'Chưa có goals cho depot. Dùng Nav2 Goal trên RViz hoặc truyền goals_json.'
            )
            self._all_goals_done = True
            return

        # --- Chờ Action Server sẵn sàng ---
        # Nav2 cần thời gian để khởi động, đặc biệt trong mô phỏng
        self.get_logger().info('⏳ Đang chờ Action Server navigate_to_pose sẵn sàng...')
        self.get_logger().info('   (Hãy đảm bảo Nav2 đã được khởi động)')

        if not self._action_client.wait_for_server(timeout_sec=60.0):
            # Nếu sau 60 giây mà action server vẫn chưa sẵn sàng -> thoát
            self.get_logger().error(
                '❌ Lỗi: Action Server navigate_to_pose không khả dụng sau 60 giây!'
            )
            self.get_logger().error(
                '   Hãy kiểm tra Nav2 đã được khởi động chưa.'
            )
            self._all_goals_done = True
            return

        self.get_logger().info('✅ Action Server navigate_to_pose đã sẵn sàng!')
        self.get_logger().info(
            f'📋 Tổng cộng {len(self.goals)} mục tiêu cần điều hướng'
        )
        self.get_logger().info('=' * 60)

        # Gửi mục tiêu đầu tiên
        self._send_next_goal()

    def _send_next_goal(self):
        """
        Gửi mục tiêu tiếp theo trong danh sách.

        Phương thức này tạo tin nhắn PoseStamped từ thông tin mục tiêu
        và gửi đến action server. Nó cũng đăng ký các callback để
        xử lý phản hồi và kết quả.
        """
        # Kiểm tra xem đã gửi hết mục tiêu chưa
        if self._current_goal_index >= len(self.goals):
            self.get_logger().info('=' * 60)
            self.get_logger().info('🎉 Đã hoàn thành tất cả các mục tiêu điều hướng!')
            self.get_logger().info('=' * 60)
            self._all_goals_done = True
            return

        # Lấy thông tin mục tiêu hiện tại
        goal_info = self.goals[self._current_goal_index]
        goal_number = self._current_goal_index + 1  # Số thứ tự (bắt đầu từ 1)

        self.get_logger().info(
            f'🚀 [{goal_number}/{len(self.goals)}] Đang gửi mục tiêu: '
            f'"{goal_info["ten"]}"'
        )
        self.get_logger().info(
            f'   📍 Tọa độ: x={goal_info["x"]:.2f}, y={goal_info["y"]:.2f}, '
            f'yaw={goal_info["yaw_deg"]:.1f}°'
        )

        # --- Tạo tin nhắn Goal ---
        goal_msg = NavigateToPose.Goal()

        # Tạo PoseStamped cho mục tiêu
        pose = PoseStamped()

        # Header: frame_id = 'map' (hệ tọa độ bản đồ)
        # Tất cả tọa độ mục tiêu phải nằm trong frame 'map'
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()

        # Vị trí (position): x, y trên mặt phẳng, z = 0 (robot di chuyển trên sàn)
        pose.pose.position.x = goal_info['x']
        pose.pose.position.y = goal_info['y']
        pose.pose.position.z = 0.0

        # Hướng (orientation): Chuyển từ góc yaw (độ) sang quaternion
        yaw_rad = math.radians(goal_info['yaw_deg'])
        qx, qy, qz, qw = euler_to_quaternion(yaw_rad)
        pose.pose.orientation.x = qx
        pose.pose.orientation.y = qy
        pose.pose.orientation.z = qz
        pose.pose.orientation.w = qw

        # Gán pose vào goal message
        goal_msg.pose = pose

        # --- Gửi Goal đến Action Server ---
        # send_goal_async: Gửi goal không đồng bộ
        # feedback_callback: Hàm được gọi khi nhận phản hồi tiến trình
        self.get_logger().info('   📤 Đang gửi goal đến Nav2...')
        send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self._feedback_callback
        )

        # Đăng ký callback khi goal được chấp nhận hoặc từ chối
        send_goal_future.add_done_callback(self._goal_response_callback)

    def _goal_response_callback(self, future):
        """
        Callback xử lý phản hồi từ action server khi nhận goal.

        Phương thức này được gọi khi action server trả lời về việc
        chấp nhận hoặc từ chối goal.

        Tham số:
            future: Future chứa kết quả phản hồi goal
        """
        goal_handle = future.result()
        goal_number = self._current_goal_index + 1

        if not goal_handle.accepted:
            # Goal bị từ chối - có thể do Nav2 đang bận hoặc goal không hợp lệ
            self.get_logger().warn(
                f'   ⚠️ [{goal_number}/{len(self.goals)}] Mục tiêu bị TỪ CHỐI!'
            )
            self.get_logger().warn(
                '   Nguyên nhân có thể: Nav2 đang bận, hoặc mục tiêu không khả thi.'
            )
            # Chuyển sang mục tiêu tiếp theo dù bị từ chối
            self._current_goal_index += 1
            self._send_next_goal()
            return

        # Goal được chấp nhận
        self.get_logger().info(
            f'   ✅ [{goal_number}/{len(self.goals)}] Mục tiêu đã được CHẤP NHẬN!'
        )
        self.get_logger().info('   🤖 Robot đang di chuyển đến mục tiêu...')

        # Chờ kết quả (robot đã đến nơi hoặc thất bại)
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self._get_result_callback)

    def _get_result_callback(self, future):
        """
        Callback xử lý kết quả cuối cùng của mục tiêu điều hướng.

        Phương thức này được gọi khi robot hoàn thành (hoặc thất bại)
        việc di chuyển đến mục tiêu.

        Tham số:
            future: Future chứa kết quả điều hướng
        """
        result = future.result()
        status = result.status
        goal_number = self._current_goal_index + 1

        if status == GoalStatus.STATUS_SUCCEEDED:
            # Robot đã đến mục tiêu thành công
            self.get_logger().info(
                f'   🎯 [{goal_number}/{len(self.goals)}] '
                f'Mục tiêu "{self.goals[self._current_goal_index]["ten"]}" - '
                f'THÀNH CÔNG!'
            )
        elif status == GoalStatus.STATUS_ABORTED:
            # Điều hướng bị hủy bỏ (không tìm được đường đi)
            self.get_logger().error(
                f'   ❌ [{goal_number}/{len(self.goals)}] '
                f'Mục tiêu "{self.goals[self._current_goal_index]["ten"]}" - '
                f'THẤT BẠI (bị hủy bỏ)!'
            )
            self.get_logger().error(
                '   Nguyên nhân: Không tìm được đường đi hoặc gặp vật cản.'
            )
        elif status == GoalStatus.STATUS_CANCELED:
            # Điều hướng bị người dùng hủy
            self.get_logger().warn(
                f'   🚫 [{goal_number}/{len(self.goals)}] '
                f'Mục tiêu "{self.goals[self._current_goal_index]["ten"]}" - '
                f'ĐÃ BỊ HỦY bởi người dùng!'
            )
        else:
            # Trạng thái không xác định
            self.get_logger().warn(
                f'   ❓ [{goal_number}/{len(self.goals)}] '
                f'Mục tiêu kết thúc với trạng thái không xác định: {status}'
            )

        self.get_logger().info('-' * 60)

        # Chuyển sang mục tiêu tiếp theo
        self._current_goal_index += 1
        self._send_next_goal()

    def _feedback_callback(self, feedback_msg):
        """
        Callback xử lý phản hồi tiến trình từ Nav2.

        Nav2 gửi phản hồi định kỳ trong quá trình điều hướng, bao gồm:
        - Vị trí hiện tại của robot
        - Thời gian ước tính còn lại
        - Khoảng cách còn lại đến mục tiêu
        - Số lượng lần phục hồi (recoveries)

        Tham số:
            feedback_msg: Tin nhắn phản hồi từ NavigateToPose action
        """
        feedback = feedback_msg.feedback

        # Lấy vị trí hiện tại của robot từ phản hồi
        current_pose = feedback.current_pose.pose
        current_x = current_pose.position.x
        current_y = current_pose.position.y

        # Lấy thời gian ước tính còn lại
        eta = feedback.estimated_time_remaining
        eta_sec = eta.sec + eta.nanosec / 1e9

        # Lấy khoảng cách còn lại
        distance = feedback.distance_remaining

        # Lấy số lần phục hồi (recovery behaviors đã thực hiện)
        recoveries = feedback.number_of_recoveries

        goal_number = self._current_goal_index + 1

        # In thông tin phản hồi (chỉ in khi khoảng cách > 0.1m để tránh spam)
        if distance > 0.1:
            self.get_logger().info(
                f'   📡 [{goal_number}/{len(self.goals)}] Phản hồi: '
                f'Vị trí=({current_x:.2f}, {current_y:.2f}), '
                f'Còn lại={distance:.2f}m, '
                f'ETA={eta_sec:.1f}s, '
                f'Phục hồi={recoveries}'
            )


def main(args=None):
    """
    Hàm chính - điểm khởi đầu của chương trình.

    Quy trình:
    1. Khởi tạo rclpy (thư viện ROS 2 Python)
    2. Tạo node SendNavGoals
    3. Gửi các mục tiêu điều hướng
    4. Quay vòng spin để xử lý callback cho đến khi hoàn thành
    5. Dọn dẹp và thoát
    """
    # Bước 1: Khởi tạo rclpy
    rclpy.init(args=args)

    # Bước 2: Tạo node
    node = SendNavGoals()

    node.get_logger().info('=' * 60)
    node.get_logger().info('🤖 CHƯƠNG TRÌNH GỬI MỤC TIÊU ĐIỀU HƯỚNG CHO NAV2')
    node.get_logger().info('   TurtleBot 4 - Depot World (Mô phỏng)')
    node.get_logger().info('=' * 60)

    try:
        # Bước 3: Gửi mục tiêu đầu tiên
        # Phương thức này sẽ chờ action server và bắt đầu gửi goals
        node.send_goals()

        # Bước 4: Spin node để xử lý các callback
        # rclpy.spin() sẽ giữ node chạy và xử lý các callback
        # (goal response, result, feedback) cho đến khi node bị tắt
        while rclpy.ok() and not node._all_goals_done:
            rclpy.spin_once(node, timeout_sec=0.5)

    except KeyboardInterrupt:
        # Người dùng nhấn Ctrl+C để dừng chương trình
        node.get_logger().info('')
        node.get_logger().info('⛔ Chương trình bị dừng bởi người dùng (Ctrl+C)')

    finally:
        # Bước 5: Dọn dẹp tài nguyên
        node.get_logger().info('🧹 Đang dọn dẹp và thoát...')
        node.destroy_node()
        rclpy.shutdown()
        print('\n👋 Tạm biệt! Chương trình đã kết thúc.')


# --- Điểm bắt đầu chương trình ---
# Khi chạy trực tiếp file Python (không qua ros2 run),
# Python sẽ gọi hàm main()
if __name__ == '__main__':
    main()

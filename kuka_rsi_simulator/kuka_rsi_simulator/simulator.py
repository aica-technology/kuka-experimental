import errno
import socket
import sys
import time
import xml.etree.ElementTree as ET

import numpy as np
import rclpy
from rclpy.node import Node


class RsiSimulator(Node):
    def __init__(self, node_name: str, host: str, port: int):
        super().__init__(node_name)
        self._cycle_time = 0.004
        self._host = host
        self._port = port
        self._q = np.array([0, -90, 90, 0, 90, 0]).astype(np.float64)
        self._wrench = np.random.rand(6,)
        self._timeout_count = 0
        self._ipoc = 0
        self._timer = self.create_timer(self._cycle_time, self.timer_callback)

        try:
            self._s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.get_logger().info("Successfully created socket")
            self._s.settimeout(1)
        except socket.error as e:
            self.get_logger().fatal(f"Could not create socket: {e}")
            sys.exit()

    def close_socket(self):
        self._s.close()

    def _create_rsi_xml_rob(self):
        root = ET.Element('Rob', {'TYPE': 'KUKA'})
        ET.SubElement(root, 'RIst', {'X': '0.0', 'Y': '0.0', 'Z': '0.0',
                                     'A': '0.0', 'B': '0.0', 'C': '0.0'})
        ET.SubElement(root, 'AIPos', {'A1': str(self._q[0]), 'A2': str(self._q[1]), 'A3': str(self._q[2]),
                                      'A4': str(self._q[3]), 'A5': str(self._q[4]), 'A6': str(self._q[5])})
        ET.SubElement(root, 'FT', {'Fx': str(self._wrench[0]), 'Fy': str(self._wrench[1]), 'Fz': str(self._wrench[2]),
                                   'Tx': str(self._wrench[3]), 'Ty': str(self._wrench[4]), 'Tz': str(self._wrench[5])})
        ET.SubElement(root, 'Delay', {'D': str(self._timeout_count)})
        ET.SubElement(root, 'IPOC').text = str(self._ipoc)
        return ET.tostring(root)

    def _parse_rsi_xml_sen(self, data):
        root = ET.fromstring(data)
        axis = root.find('Axis').attrib
        desired_joint_correction = np.array([axis['A1'], axis['A2'], axis['A3'],
                                             axis['A4'], axis['A5'], axis['A6']]).astype(np.float64)
        if self._ipoc != int(root.find('IPOC').text):
            raise
        return desired_joint_correction

    def timer_callback(self):
        try:
            msg = self._create_rsi_xml_rob()
            self._s.sendto(msg, (self._host, self._port))
            recv_msg, addr = self._s.recvfrom(1024)
            des_joint_correction = self._parse_rsi_xml_sen(recv_msg)
            self._q += des_joint_correction
            self._wrench = np.random.rand(6,)
            self._ipoc += 1
            time.sleep(self._cycle_time / 2)
        except socket.timeout as e:
            self.get_logger().warn("Socket timed out")
            self._timeout_count += 1
        except socket.error as e:
            if e.errno != errno.EINTR:
                raise


def main():
    import argparse

    parser = argparse.ArgumentParser(description='RSI Simulation')
    parser.add_argument('rsi_hw_iface_ip', help='The ip address of the RSI control interface')
    parser.add_argument('rsi_hw_iface_port', help='The port of the RSI control interface')
    # Only parse known arguments
    args, _ = parser.parse_known_args()
    host = args.rsi_hw_iface_ip
    port = int(args.rsi_hw_iface_port)

    rclpy.init()
    rsi_sim = RsiSimulator("rsi_simulator", host, port)
    try:
        rclpy.spin(rsi_sim)
    except KeyboardInterrupt:
        pass
    rsi_sim.close_socket()
    rsi_sim.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()

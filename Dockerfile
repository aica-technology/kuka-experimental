ARG BASE_TAG=latest
FROM ghcr.io/aica-technology/component-sdk:${BASE_TAG}
WORKDIR ${WORKSPACE}

RUN sudo apt update && sudo apt install -y ros-${ROS_DISTRO}-joint-state-publisher-gui

COPY --chown=${USER} ./kuka_rsi_simulator ./src/kuka_rsi_simulator
COPY --chown=${USER} ./kuka_kr16_support ./src/kuka_kr16_support
RUN source ${WORKSPACE}/install/setup.bash; colcon build --symlink-install

# clean image
RUN sudo apt-get clean && sudo rm -rf /var/lib/apt/lists/* && sudo rm -rf /tmp/*